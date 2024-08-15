from datetime import datetime
from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV, Item, History, Warehouse, HistoryIncrement
from accounts.models import User, Group, Meeting
from django.db.models import Q
from .filters import TaskFilter
from django.db.models import Count
from datetime import date


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class InternetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internet
        fields = '__all__'


class InternetUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internet
        fields = '__all__'


class TVSerializer(serializers.ModelSerializer):
    class Meta:
        model = TV
        fields = '__all__'


class TVUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TV
        fields = '__all__'


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'


class VoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else None

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else None

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_user_type(self, obj):
        return obj.user.user_type if obj.user else None


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskDetailSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True)
    tv = TVSerializer()
    internet = InternetSerializer()
    voice = VoiceSerializer()
    services = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'user', 'full_name', 'task_type', 'registration_number',
            'contact_number', 'location', 'note', 'date', 'start_time', 'end_time', 'status',
            'tv', 'voice', 'internet', 'services', 'first_name', 'last_name', 'phone', 'group', "is_tv", "is_voice", "is_internet"
        ]

    def get_services(self, obj):
        try:
            return obj.get_service()
        except Exception as e:
            print(f"Error getting services: {e}")
            return None

    def get_first_name(self, obj):
        try:
            return obj.user.first_name if obj.user else None
        except AttributeError as e:
            print(f"Error getting first name: {e}")
            return None

    def get_last_name(self, obj):
        try:
            return obj.user.last_name if obj.user else None
        except AttributeError as e:
            print(f"Error getting last name: {e}")
            return None

    def get_phone(self, obj):
        try:
            return obj.user.phone if obj.user else None
        except AttributeError as e:
            print(f"Error getting phone: {e}")
            return None


class PerformanceSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_type', 'first_name',
                  'last_name', 'group', 'task_count']

    def get_group(self, obj):
        group_data = {}
        if obj.group:
            group_data = {
                'id': obj.group.id,
                'group': obj.group.group,
                'region': obj.group.region
            }
        return group_data

    def get_task_count(self, obj):
        start_date = self.context['request'].query_params.get('start_date')
        end_date = self.context['request'].query_params.get('end_date')

        task_query = Task.objects.filter(user=obj)

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                task_query = task_query.filter(date__gte=start_date)
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid start_date format. Use YYYY-MM-DD.")

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                task_query = task_query.filter(date__lte=end_date)
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid end_date format. Use YYYY-MM-DD.")

        task_counts = task_query.values(
            'task_type').annotate(count=Count('id'))

        counts_dict = {count['task_type']: count['count']
                       for count in task_counts}

        sorted_counts = sorted(counts_dict.items(),
                               key=lambda x: x[1], reverse=True)

        sorted_task_types, sorted_task_counts = zip(
            *sorted_counts) if sorted_counts else ([], [])

        return {
            'total': sum(sorted_task_counts),
            'connection': sorted_task_counts[sorted_task_types.index('connection')] if 'connection' in sorted_task_types else 0,
            'problem': sorted_task_counts[sorted_task_types.index('problem')] if 'problem' in sorted_task_types else 0
        }


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['created_by']


class DecrementItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    company = serializers.CharField(
        max_length=255, required=False, allow_blank=True)
    authorized_person = serializers.CharField(
        max_length=255, required=False, allow_blank=True)
    number = serializers.IntegerField()
    texnik_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(
        user_type='Texnik'), required=False, allow_null=True)

    def validate(self, data):
        company = data.get('company')
        authorized_person = data.get('authorized_person')
        texnik_user = data.get('texnik_user')

        if not (company or authorized_person or texnik_user):
            raise serializers.ValidationError(
                "At least one of 'company', 'authorized_person', or 'texnik_user' must be provided.")

        return data


class ItemUserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'group']


class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class HistorySerializer(serializers.ModelSerializer):
    item_warehouse = WarehouseSerializer()
    texnik_user = ItemUserSerializer()
    item_created_by = UserHistorySerializer(read_only=True)

    class Meta:
        model = History
        fields = '__all__'


class HistoryIncrementSerializer(serializers.ModelSerializer):
    item_warehouse = WarehouseSerializer()
    item_created_by = UserHistorySerializer(read_only=True)

    class Meta:
        model = HistoryIncrement
        fields = '__all__'


class IncrementItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    product_provider = serializers.CharField(max_length=255, required=True)
    number = serializers.IntegerField()

    def validate(self, data):
        if data['number'] <= 0:
            raise serializers.ValidationError(
                "The increment number must be positive.")
        return data


class WarehouseItemSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()
    created_by = ItemUserSerializer()

    class Meta:
        model = Item
        fields = '__all__'


class CreatingMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

################################################################################################


class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        exclude = ['participants']


class MeetingDetailSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = '__all__'

    def get_participants(self, obj):
        return [f"{participant.first_name} {participant.last_name}" for participant in obj.participants.all()]


class MainPageUserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    task_details = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    ongoing_tasks = serializers.SerializerMethodField()
    meetings = MeetingSerializer(many=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'group', 'user_type', 'is_staff',
                  'is_superuser', 'task_details', 'completed_tasks', 'meetings', 'ongoing_tasks')

    def get_task_details(self, obj):
        if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(
                task_type='connection').count()
            response = {
                'problem_count': problem_count,
                'connection_count': connection_count
            }
        elif obj.is_staff or obj.is_superuser:
            tv_task_count = Task.objects.filter(is_tv=True).count()
            internet_task_count = Task.objects.filter(is_internet=True).count()
            voice_task_count = Task.objects.filter(is_voice=True).count()
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(
                task_type='connection').count()

            response = {
                'tv_count': tv_task_count,
                'internet_count': internet_task_count,
                'voice_count': voice_task_count,
                'problem_count': problem_count,
                'connection_count': connection_count
            }
        else:
            tv_task_count = Task.objects.filter(user=obj, is_tv=True).count()
            internet_task_count = Task.objects.filter(
                user=obj, is_internet=True).count()
            voice_task_count = Task.objects.filter(
                user=obj, is_voice=True).count()
            response = {
                'tv_count': tv_task_count,
                'internet_count': internet_task_count,
                'voice_count': voice_task_count
            }
        return response

    def get_completed_tasks(self, obj):
        if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
            completed_tasks = Task.objects.filter(
                user=obj, status__in=['completed'])
        else:
            completed_tasks = Task.objects.filter(status__in=['completed'])
        data = TaskSerializer(completed_tasks, many=True).data
        return data

    def get_ongoing_tasks(self, obj):
        if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
            ongoing_tasks = Task.objects.filter(
                user=obj, status__in=['started', 'inprogress'])
        else:
            ongoing_tasks = Task.objects.filter(
                status__in=['started', 'inprogress'])
        data = TaskSerializer(ongoing_tasks, many=True).data
        return data


class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['user', 'status']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.user = request.user
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance


class UpdateTaskSerializer(serializers.ModelSerializer):
    tv = TVSerializer()
    internet = InternetSerializer()
    voice = VoiceSerializer()
    services = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['task_type', 'full_name', 'start_time', 'end_time', 'registration_number', 'contact_number', 'location',
                  'services', 'status', 'group', 'note', "is_tv", "is_voice", "is_internet",  'date', 'tv', 'voice', 'internet']

    def get_services(self, obj):
        try:
            return obj.get_service()
        except Exception as e:
            print(f"Error getting services: {e}")
            return None
