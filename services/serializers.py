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
    class Meta:
        model = History
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
        fields = ('first_name','last_name','group','user_type','task_details','ongoing_tasks','meetings')

    def get_task_details(self,obj):
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
        ongoing_tasks = Task.objects.filter(user=obj, status__in=['started', 'inprogress'])
        data = TaskSerializer(ongoing_tasks,many=True).data
        return data
    

class CreateTaskSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Task
        fields = '__all__'
