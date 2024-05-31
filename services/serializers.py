from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV, Warehouse, History
from accounts.models import User,Group,Meeting
from django.db.models import Q
from .filters import TaskFilter

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class InternetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internet
        fields = '__all__'

class TVSerializer(serializers.ModelSerializer):
    class Meta:
        model = TV
        fields = '__all__'

class VoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voice
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=True)
    class Meta:
        model = Task
        fields = '__all__'

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    

class TaskDetailSerializer(serializers.ModelSerializer):
    tv = TVSerializer()
    internet = InternetSerializer()
    voice = VoiceSerializer()

    services = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'user', 'task_type', 'description', 'registration_number', 'contact_number', 'location', 'note', 'date', 'status', 'tv', 'voice', 'internet', 'services']

    def get_services(self, obj):
        return obj.get_service()


class PerformanceSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'user_type', 'first_name', 'last_name', 'group', 'task_count']

    def get_task_count(self, obj):
        total = Task.objects.filter(user=obj).count()
        connection = Task.objects.filter(user=obj,task_type='connection').count()
        problem = Task.objects.filter(user=obj,task_type='problem').count()
        data = {
            'total':total,
            'connection':connection,
            'problem':problem
        }
        return data

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'

class HistorySerializer(serializers.ModelSerializer):
    equipment_name = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    serial_number = serializers.SerializerMethodField()
    region = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()
    size_length = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = ['equipment_name', 'brand', 'model', 'serial_number', 'region', 'number', 'size_length', 'action', 'timestamp']

    def get_equipment_name(self, obj):
        try:
            return obj.warehouse_item.equipment_name
        except AttributeError:
            return "Deleted"

    def get_brand(self, obj):
        try:
            return obj.warehouse_item.brand
        except AttributeError:
            return "Deleted"

    def get_model(self, obj):
        try:
            return obj.warehouse_item.model
        except AttributeError:
            return "Deleted"

    def get_serial_number(self, obj):
        try:
            return obj.warehouse_item.serial_number
        except AttributeError:
            return "Deleted"

    def get_region(self, obj):
        try:
            return obj.warehouse_item.region
        except AttributeError:
            return "Deleted"

    def get_number(self, obj):
        try:
            return obj.warehouse_item.number
        except AttributeError:
            return "Deleted"

    def get_size_length(self, obj):
        try:
            return obj.warehouse_item.size_length
        except AttributeError:
            return "Deleted"


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
        fields = ('first_name','last_name','group','user_type','task_details','ongoing_tasks','meetings')

    def get_task_details(self,obj):
        if obj.user_type == 'technician' or obj.user_type == 'plumber':
            tv_task_count = Task.objects.filter(user=obj, is_tv=True).count()
            internet_task_count = Task.objects.filter(user=obj, is_internet=True).count()
            voice_task_count = Task.objects.filter(user=obj, is_voice=True).count()

            response = {
                'tv_count':tv_task_count,
                'internet_count':internet_task_count,
                'voice_count':voice_task_count,
            }
        else:
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(task_type='connection').count()
            
            response = {
                'problem_count':problem_count,
                'connection_count':connection_count
            }
        return response
    
    def get_ongoing_tasks(self,obj):
        if obj.user_type == 'technician' or obj.user_type == 'plumber':
            ongoing_tasks = Task.objects.filter(user=obj, status__in=['started', 'inprogress'])
        else:
            ongoing_tasks = Task.objects.filter(status__in=['started', 'inprogress'])
        data = TaskSerializer(ongoing_tasks,many=True).data
        return data
    

class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Task
        fields = '__all__'