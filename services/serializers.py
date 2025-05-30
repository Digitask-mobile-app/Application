from datetime import datetime
from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV, WarehouseChange, Internet_packages
from accounts.models import User, Group, Meeting
from django.db.models import Q
from .filters import TaskFilter
from django.db.models import Count
from datetime import date
from django.utils import timezone
from warehouse.serializers import ItemSerializer


class InternetPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internet_packages
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group', 'region', 'region_name']


class InternetSerializer(serializers.ModelSerializer):
    internet_packs = InternetPackSerializer()

    class Meta:
        model = Internet
        fields = '__all__'


class CreateInternetSerializer(serializers.ModelSerializer):
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


class TVUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TV
        fields = ['id', 'photo_modem']


class InternetUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internet
        fields = ['id', 'photo_modem']


class VoiceUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = ['id', 'photo_modem']


class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'


class VoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'


class WarehouseChangeTaskSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.SerializerMethodField()
    item = ItemSerializer()

    class Meta:
        model = WarehouseChange
        fields = '__all__'

    def get_warehouse_name(self, obj):
        return obj.item.warehouse.name if obj.item and obj.item.warehouse else None


class TaskSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    has_internet = serializers.SerializerMethodField()
    has_voice = serializers.SerializerMethodField()
    has_tv = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else None

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else None

    def get_email(self, obj):
        return obj.user.email if obj.user else None

    def get_has_internet(self, obj):
        return hasattr(obj, 'internet') and obj.internet is not None

    def get_has_voice(self, obj):
        return hasattr(obj, 'voice') and obj.voice is not None

    def get_has_tv(self, obj):
        return hasattr(obj, 'tv') and obj.tv is not None


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
    has_internet = serializers.SerializerMethodField()
    has_voice = serializers.SerializerMethodField()
    has_tv = serializers.SerializerMethodField()
    task_items = WarehouseChangeTaskSerializer(many=True)

    class Meta:
        model = Task
        fields = [
            'id', 'user', 'full_name', 'task_type', 'registration_number',
            'contact_number', 'location', 'note', 'date', 'end_date', 'start_time', 'end_time', 'status',
            'tv', 'voice', 'internet', 'services', 'first_name', 'last_name', 'phone', 'group', 'latitude', 'longitude',
            "is_tv", "is_voice", "is_internet", "passport", 'has_tv', 'has_voice', 'has_internet',
            'task_items'
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

    def get_has_internet(self, obj):
        return hasattr(obj, 'internet') and obj.internet is not None

    def get_has_voice(self, obj):
        return hasattr(obj, 'voice') and obj.voice is not None

    def get_has_tv(self, obj):
        return hasattr(obj, 'tv') and obj.tv is not None


class PerformanceSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    position_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'position_name', 'first_name',
                  'last_name', 'group', 'task_count']

    def get_group(self, obj):
        group_data = {}
        if obj.group:
            group_data = {
                'id': obj.group.id,
                'group': obj.group.group,
                'region': str(obj.group.region) if obj.group.region else None
            }
        return group_data

    def get_position_name(self, obj):
        position = {}
        if obj.position and obj.position.name:
            position['name'] = obj.position.name
            position['id'] = obj.position.id
        return position

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
    waiting_tasks = serializers.SerializerMethodField()
    meetings = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'group', 'position', 'is_staff',
                  'is_superuser', 'task_details', 'completed_tasks', 'meetings', 'ongoing_tasks', 'waiting_tasks')

    def get_task_details(self, obj):
        # if obj.position.name == 'Texnik' or obj.position == 'Plumber':
        #     problem_count = Task.objects.filter(task_type='problem').count()
        #     connection_count = Task.objects.filter(
        #         task_type='connection').count()
        #     response = {
        #         'problem_count': problem_count,
        #         'connection_count': connection_count
        #     }
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
        # else:
        #     tv_task_count = Task.objects.filter(user=obj, is_tv=True).count()
        #     internet_task_count = Task.objects.filter(
        #         user=obj, is_internet=True).count()
        #     voice_task_count = Task.objects.filter(
        #         user=obj, is_voice=True).count()
        #     response = {
        #         'tv_count': tv_task_count,
        #         'internet_count': internet_task_count,
        #         'voice_count': voice_task_count
        #     }
        return response

    def get_completed_tasks(self, obj):
        # if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
        #     completed_tasks = Task.objects.filter(
        #         user=obj, status__in=['completed'])
        # else:
        completed_tasks = Task.objects.filter(status__in=['completed'])
        data = TaskSerializer(completed_tasks, many=True).data
        return data

    def get_ongoing_tasks(self, obj):
        # if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
        #     ongoing_tasks = Task.objects.filter(
        #         user=obj, status__in=['started', 'inprogress'])
        # else:
        ongoing_tasks = Task.objects.filter(
            status__in=['started', 'inprogress'])
        data = TaskSerializer(ongoing_tasks, many=True).data
        return data

    def get_waiting_tasks(self, obj):
        waiting_tasks = Task.objects.filter(status__in=['waiting'])

        if waiting_tasks.exists():
            data = TaskSerializer(waiting_tasks, many=True).data
        else:
            all_tasks = Task.objects.all()
            data = TaskSerializer(all_tasks, many=True).data

        return data

    def get_meetings(self, obj):
        now = timezone.now()
        # Filter meetings to include only those that are in the future
        upcoming_meetings = Meeting.objects.filter(
            participants=obj, date__gte=now)
        data = MeetingSerializer(upcoming_meetings, many=True).data
        return data


class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def to_internal_value(self, data):
        # `group[]` verisini işlemek için elle çekiyoruz
        groups = data.getlist('group[]')  # group[]'leri liste olarak alıyoruz
        data._mutable = True  # Eğer QueryDict immutable ise değiştirilebilir yapıyoruz
        # group[]'leri 'group' anahtarına atıyoruz
        data.setlist('group', groups)
        return super().to_internal_value(data)

    def create(self, validated_data):
        # Many-to-Many alanını çıkart
        groups = validated_data.pop('group', None)

        # Task nesnesini oluştur
        task = Task.objects.create(**validated_data)

        # Eğer groups varsa Many-to-Many ilişkisini ayarla
        if groups:
            task.group.set(groups)
        return task


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status']

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
                  'services', 'status', 'group', 'note', "is_tv", "is_voice", "is_internet",  'date', 'end_date', 'latitude', 'longitude',
                  'tv', 'voice', 'internet']

    def get_services(self, obj):
        try:
            return obj.get_service()
        except Exception as e:
            print(f"Error getting services: {e}")
            return None


class UpdateTaskImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'passport']


class WarehouseChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseChange
        fields = '__all__'


class WarehouseBulkChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WarehouseChange
        exclude = ['delivery_note']


class MapTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['full_name', 'registration_number', 'latitude', 'longitude']
