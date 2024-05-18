from .models import Task
from .serializers import TaskSerializer, TaskDetailSerializer
from .filters import StatusAndTaskFilter
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView


class CreateTaskView(generics.CreateAPIView):
    serializer_class = TaskDetailSerializer


class TaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer

class TaskDetailView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filterset_class = StatusAndTaskFilter
    filter_backends = (DjangoFilterBackend,)

    

class UserTaskListView(APIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(user=user)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        connection_completed_count = queryset.filter(task_type='connection', status='completed').count()
        problem_completed_count = queryset.filter(task_type='problem', status='completed').count()
        completed_count = queryset.filter(status='completed').count()

        context = {
            'connection_completed_count': connection_completed_count,
            'problem_completed_count': problem_completed_count,
            'completed_count': completed_count
        }

        serializer = self.serializer_class(queryset, many=True)
        response_data = {
            'tasks': serializer.data,
            'summary': context
        }

        return Response(response_data, status=status.HTTP_200_OK)