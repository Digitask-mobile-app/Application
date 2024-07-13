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
    id = serializers.CharField(source='user.id')
    user_type = serializers.CharField(source='user.user_type')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    group = serializers.SerializerMethodField()
    task_count = serializers.SerializerMethodField()
    dates = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'user_type', 'first_name', 'last_name', 'group', 'task_count', 'dates']

    def get_group(self, obj):
        group_data = {}
        if obj.user and obj.user.group:
            group_data = {
                'id': obj.user.group.id,
                'group': obj.user.group.group,
                'region': obj.user.group.region
            }
        return group_data

    def get_task_count(self, obj):
        if obj.user:
            task_counts = Task.objects.filter(user=obj.user).values('task_type').annotate(count=Count('id'))
            total_count = sum([count['count'] for count in task_counts])
            connection_count = next((count['count'] for count in task_counts if count['task_type'] == 'connection'), 0)
            problem_count = next((count['count'] for count in task_counts if count['task_type'] == 'problem'), 0)

            return {
                'total': total_count,
                'connection': connection_count,
                'problem': problem_count
            }
        else:
            return {
                'total': 0,
                'connection': 0,
                'problem': 0
            }

    def get_dates(self, obj):
        dates = Task.objects.filter(user=obj.user).order_by('date').values_list('date', flat=True)
        return list(dates)



    
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
    mac = serializers.SerializerMethodField()
    port_number = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = ['id', 'warehouse', 'equipment_name', 'brand', 'model', 'serial_number', 'number', 'mac', 'port_number', 'size_length', 'action', 'timestamp']

    def create(self, validated_data):
        validated_data['action'] = 'export'
        instance = super().create(validated_data)

        try:
            warehouse_item = instance.warehouse_item
            if warehouse_item.number > 0:
                warehouse_item.number -= 1
                warehouse_item.save()

            instance.number = validated_data['number']
            instance.save()

        except Exception as e:
            pass

        return instance

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
            return obj.number  
        except AttributeError:
            return "Deleted"

    def get_size_length(self, obj):
        try:
            return obj.warehouse_item.size_length
        except AttributeError:
            return "Deleted"
        
    def get_port_number(self, obj):
        try:
            return obj.warehouse_item.port_number
        except AttributeError:
            return "Deleted"
        
    def get_mac(self, obj):
        try:
            return obj.warehouse_item.mac
        except AttributeError:
            return "Deleted"

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
        fields = ('first_name', 'last_name', 'group', 'user_type', 'task_details', 'ongoing_tasks', 'meetings')

    def get_task_details(self, obj):
        if obj.user_type == 'texnik' or obj.user_type == 'plumber':
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
            response = {
                'tv_count': tv_task_count,
                'internet_count': internet_task_count,
                'voice_count': voice_task_count
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
        if obj.user_type == 'texnik' or obj.user_type == 'plumber':
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