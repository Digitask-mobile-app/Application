from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV, Item, History, Warehouse
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
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_first_name(self, obj):
        return obj.user.first_name if obj.user else None

    def get_last_name(self, obj):
        return obj.user.last_name if obj.user else None

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
            'tv', 'voice', 'internet', 'services', 'first_name', 'last_name', 'phone','group'
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
    warehouse = serializers.SerializerMethodField()
    equipment_name = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    serial_number = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()
    size_length = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = ['warehouse', 'equipment_name', 'brand', 'model', 'serial_number', 'number', 'size_length', 'action', 'timestamp']

    def get_warehouse(self, obj):
        try:
            warehouse_item = obj.warehouse_item
            warehouse_data = {
                'name': warehouse_item.warehouse.name,
                'region': warehouse_item.warehouse.region
            }
            return warehouse_data
        except AttributeError:
            return "Deleted"
    
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
            problem_count = Task.objects.filter(task_type='problem').count()
            connection_count = Task.objects.filter(task_type='connection').count()
            
            response = {
                'problem_count':problem_count,
                'connection_count':connection_count
            }
        else:
            tv_task_count = Task.objects.filter(user=obj, is_tv=True).count()
            internet_task_count = Task.objects.filter(user=obj, is_internet=True).count()
            voice_task_count = Task.objects.filter(user=obj, is_voice=True).count()

            response = {
                'tv_count':tv_task_count,
                'internet_count':internet_task_count,
                'voice_count':voice_task_count,
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
