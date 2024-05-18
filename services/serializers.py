from rest_framework import serializers, viewsets
from .models import Task, Internet, Voice, TV
from accounts.models import User

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
    class Meta:
        model = Task
        fields = ['id', 'registration_number', 'note', 'date', 'status', 'contact_number']

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
        fields = ['id', 'user', 'task_type', 'description', 'registration_number', 'contact_number', 'photo_ID', 'location', 'note', 'date', 'status', 'tv', 'voice', 'internet', 'services']

    def get_services(self, obj):
        return obj.get_service()

    
