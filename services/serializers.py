from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV, Item, History, Warehouse
from accounts.models import User,Group,Meeting
from django.db.models import Q
from .filters import TaskFilter
from django.db.models import Count


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
            'contact_number', 'location', 'note', 'date', 'time', 'status',
            'tv', 'voice', 'internet', 'services', 'first_name', 'last_name', 'phone','group',"is_tv", "is_voice", "is_internet"
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
    dates = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_type', 'first_name', 'last_name', 'group', 'task_count', 'dates']

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
            task_query = task_query.filter(date__gte=start_date)
        if end_date:
            task_query = task_query.filter(date__lte=end_date)

        task_counts = task_query.values('task_type').annotate(count=Count('id'))
        total_count = sum([count['count'] for count in task_counts])
        connection_count = next((count['count'] for count in task_counts if count['task_type'] == 'connection'), 0)
        problem_count = next((count['count'] for count in task_counts if count['task_type'] == 'problem'), 0)

        return {
            'total': total_count,
            'connection': connection_count,
            'problem': problem_count
        }

    def get_dates(self, obj):
        start_date = self.context['request'].query_params.get('start_date')
        end_date = self.context['request'].query_params.get('end_date')
        task_query = Task.objects.filter(user=obj).order_by('date')
        if start_date:
            task_query = task_query.filter(date__gte=start_date)
        if end_date:
            task_query = task_query.filter(date__lte=end_date)

        dates = list(task_query.values_list('date', flat=True))
        return dates

    
class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class WarehouseItemSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()
    class Meta:
        model = Item
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

class DecrementItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField()
    company = serializers.CharField(max_length=255)
    authorized_person = serializers.CharField(max_length=255)
    number = serializers.IntegerField()
    texnik_user = serializers.IntegerField()
    date = serializers.DateField()

class TexnikUserSerializer(serializers.ModelSerializer):
    group= GroupSerializer()
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'group']

class CreatingMeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

################################################################################################

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        exclude = ['participants']


class MainPageUserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    task_details = serializers.SerializerMethodField()
    ongoing_tasks = serializers.SerializerMethodField()
    meetings = MeetingSerializer(many=True)

    class Meta: 
        model = User
        fields = ('first_name', 'last_name', 'group', 'user_type', 'is_staff', 'is_superuser', 'task_details', 'ongoing_tasks', 'meetings')

    def get_task_details(self, obj):
        if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(task_type='connection').count()
            response = {
                'problem_count': problem_count,
                'connection_count': connection_count
            }
        elif obj.is_staff or obj.is_superuser:
            tv_task_count = Task.objects.filter(is_tv=True).count()
            internet_task_count = Task.objects.filter(is_internet=True).count()
            voice_task_count = Task.objects.filter(is_voice=True).count()
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(task_type='connection').count()

            response = {
                'tv_count': tv_task_count,
                'internet_count': internet_task_count,
                'voice_count': voice_task_count,
                'problem_count': problem_count,
                'connection_count': connection_count
            }
        else:
            tv_task_count = Task.objects.filter(user=obj, is_tv=True).count()
            internet_task_count = Task.objects.filter(user=obj, is_internet=True).count()
            voice_task_count = Task.objects.filter(user=obj, is_voice=True).count()
            response = {
                'tv_count': tv_task_count,
                'internet_count': internet_task_count,
                'voice_count': voice_task_count
            }
        return response

    def get_ongoing_tasks(self, obj):
        if obj.user_type == 'Texnik' or obj.user_type == 'Plumber':
            ongoing_tasks = Task.objects.filter(user=obj, status__in=['started', 'inprogress'])
        else:
            ongoing_tasks = Task.objects.filter(status__in=['started', 'inprogress'])
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
        fields = ['task_type', 'full_name', 'time', 'registration_number', 'contact_number', 'location', 'services', 'status', 'group', 'note', "is_tv", "is_voice", "is_internet", 'tv', 'voice', 'internet', ]

    def get_services(self, obj):
        try:
            return obj.get_service()
        except Exception as e:
            print(f"Error getting services: {e}")
            return None