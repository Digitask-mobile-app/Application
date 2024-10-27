from django.utils import timezone
from django.http import JsonResponse
from .models import Task,WarehouseChange
from .serializers import *
from .filters import StatusAndTaskFilter,TaskWarehouseFilter
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from accounts.serializers import UserSerializer
from accounts.models import Notification
from warehouse.models import Item,Warehouse, WarehouseHistory

class CreateTaskView(generics.CreateAPIView):
    serializer_class = TaskDetailSerializer


class CreateGroupView(generics.CreateAPIView):
    serializer_class = GroupSerializer


class TaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer


class GroupListView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TaskDetailView(RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


class TaskListAPIView(generics.ListAPIView):
    queryset = Task.objects.all().order_by('-created_at')
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
        serializer = self.serializer_class(queryset, many=True)
        response_data = {
            'tasks': serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PerformanceListView(generics.ListAPIView):
    serializer_class = PerformanceSerializer
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        queryset = User.objects.filter(user_type="Texnik")

        users_with_totals = []

        for user in queryset:
            context = {'request': self.request}

            serializer = PerformanceSerializer(user, context=context)
            task_count = serializer.data['task_count']

            total = task_count['total']
            users_with_totals.append((user, total))

        sorted_users = sorted(
            users_with_totals, key=lambda x: x[1], reverse=True)

        sorted_queryset = [user for user, _ in sorted_users]

        return sorted_queryset




class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
    http_method_names = ['patch']

class TaskImageUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskImageSerializer
    http_method_names = ['patch']



class CreateMeetingView(generics.CreateAPIView):
    serializer_class = CreatingMeetingSerializer
    queryset = Meeting.objects.all()


class MeetingDetailView(generics.RetrieveAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingDetailSerializer
    lookup_field = 'id'


class TaskDeleteAPIView(APIView):
    def delete(self, request, id):
        try:
            task = Task.objects.get(pk=id)
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

#####################################################################################################################


class MainPageView(generics.RetrieveAPIView):
    serializer_class = MainPageUserSerializer

    def get_object(self):
        return self.request.user


class CreateTaskView(generics.CreateAPIView):
    serializer_class = CreateTaskSerializer
    queryset = Task.objects.all()


class CreateTvView(generics.CreateAPIView):
    queryset = TV.objects.all()
    serializer_class = TVSerializer


class UpdateTvView(generics.UpdateAPIView):
    queryset = TV.objects.all()
    serializer_class = TVUpdateSerializer
    http_method_names = ['patch']


class CreateInternetView(generics.CreateAPIView):
    queryset = Internet.objects.all()
    serializer_class = InternetSerializer


class UpdateInternetView(generics.UpdateAPIView):
    queryset = Internet.objects.all()
    serializer_class = InternetUpdateSerializer
    http_method_names = ['patch']


class CreateVoiceView(generics.CreateAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceSerializer


class UpdateVoiceView(generics.UpdateAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceUpdateSerializer
    http_method_names = ['patch']


class UpdateTaskView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['patch']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        instance = serializer.save()
        instance = self.get_object()
        user = self.request.user
        self.create_status_notification(instance, user)
       

    def create_status_notification(self, task_instance, user):
        if task_instance.status == 'inprogress':
            message = f' istifadəçi {task_instance.full_name} adlı müştərinin tapşırığını qəbul etdi.'
        elif task_instance.status == 'started':
            message = f' istifadəçi {task_instance.full_name} adlı müştərinin tapşırığının icrasına başladı.'
        elif task_instance.status == 'completed':
            message = f' istifadəçi {task_instance.full_name} adlı müştərinin tapşırığını uğurla başa vurdu.'
     
            self.warehouse_item_decrement(task_instance,user)
         
        else:
            message = f' istifadəçi {task_instance.full_name} adlı müştərinin tapşırığında {task_instance.status} statusuna keçid etdi.'

        notification = Notification.objects.create(
            message=message, 
            user_email=user.email
        )
        
        texnik_users = User.objects.filter(user_type='Ofis menecer')
        plumber_users = User.objects.filter(user_type='Texnik menecer')
        notification.users.set(texnik_users | plumber_users)
        notification.save()

    def warehouse_item_decrement(self, task_instance, user):
        warehouse_changes = task_instance.task_items.all()
     
        for change in warehouse_changes:
            current_count = change.item.count
            new_count = max(0, current_count - change.count) 
            change.item.count = new_count
            change.item.save()
        
            WarehouseHistory.objects.create(
                item=change.item,
                modified_by=user,
                action='decrement',
                old_count=current_count,
                new_count=new_count,
                task = task_instance,
                is_tv = change.is_tv,
                is_internet = change.is_internet,
                is_voice = change.is_voice
            )
            



def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)


class MeetingsApiView(generics.ListAPIView):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        now = timezone.now()
        return Meeting.objects.filter(date__gte=now)

class WarehouseChangeViewSet(viewsets.ModelViewSet):
    queryset = WarehouseChange.objects.all()
    serializer_class = WarehouseChangeSerializer

class TaskWarehouseListView(generics.ListAPIView):
    queryset = WarehouseChange.objects.all()
    serializer_class = WarehouseChangeSerializer
    filterset_class = TaskWarehouseFilter
    filter_backends = (DjangoFilterBackend,)