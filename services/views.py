from django.utils.timezone import now
from django.db.models.functions import TruncDay, TruncMonth
from django.utils import timezone
from django.http import JsonResponse
from .models import Task, WarehouseChange
from .serializers import *
from .filters import StatusAndTaskFilter, TaskWarehouseFilter
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from accounts.models import Notification
from warehouse.models import WarehouseHistory

# class CreateTaskView(generics.CreateAPIView):
#     serializer_class = CreateTaskSerializer

#     def perform_create(self, serializer):
#         instance = serializer.save()
#         self.create_status_notification(instance)


#     def create_status_notification(self, task_instance):
#         message = f'Yeni tapşırıq əlavə edildi. Qeydiyyat nömrəsi {task_instance.registration_number} Tapşırıq siyahısını nəzərdən keçirməniz rica olunur!'
#         notification = Notification.objects.create(
#             task=task_instance,
#             message=message,
#             action='create'
#         )

#         texnik_users = User.objects.filter(user_type='Ofis menecer')
#         plumber_users = User.objects.filter(user_type='Texnik menecer')
#         notification.users.set(texnik_users | plumber_users)
#         notification.save()
# ssssssssssssssssssssssssssssssss


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
        queryset = User.objects.all()

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

    def perform_create(self, serializer):
        instance = serializer.save()
        self.create_status_notification(instance)

    def create_status_notification(self, task_instance):
        message = f'Yeni tapşırıq əlavə edildi. Qeydiyyat nömrəsi {task_instance.registration_number} Tapşırıq siyahısını nəzərdən keçirməniz rica olunur!'
        report = f'Yeni {task_instance.task_type} tapşırığı əlavə olundu.Xidmət növü {task_instance.get_service()}, qeydiyyat nömrəsi isə {task_instance.registration_number}'
        notification = Notification.objects.create(
            task=task_instance,
            message=message,
            action='create',
            report=report
        )

        notification.users.set(User.objects.all())
        notification.save()


class CreateTvView(generics.CreateAPIView):
    queryset = TV.objects.all()
    serializer_class = TVSerializer


class UpdateTvView(generics.UpdateAPIView):
    queryset = TV.objects.all()
    serializer_class = TVUpdateSerializer
    http_method_names = ['patch']


class UpdateTvImageView(generics.UpdateAPIView):
    queryset = TV.objects.all()
    serializer_class = TVUpdateImageSerializer
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        if 'photo_modem' not in request.data:
            return Response({'error': 'photo_modem field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        photo_file = request.FILES.get('photo_modem')
        if not photo_file or not photo_file.content_type.startswith('image/'):
            return Response({'error': 'Invalid file type. Only image files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = self.get_object()
        if updated_instance.photo_modem != photo_file.name:
            return Response({'error': 'Failed to update photo_modem field.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response


class UpdateInternetImageView(generics.UpdateAPIView):
    queryset = Internet.objects.all()
    serializer_class = InternetUpdateImageSerializer
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        if 'photo_modem' not in request.data:
            return Response({'error': 'photo_modem field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        photo_file = request.FILES.get('photo_modem')
        if not photo_file or not photo_file.content_type.startswith('image/'):
            return Response({'error': 'Invalid file type. Only image files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = self.get_object()
        if updated_instance.photo_modem != photo_file.name:
            return Response({'error': 'Failed to update photo_modem field.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response


class UpdateVoiceImageView(generics.UpdateAPIView):
    queryset = Voice.objects.all()
    serializer_class = VoiceUpdateImageSerializer
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        if 'photo_modem' not in request.data:
            return Response({'error': 'photo_modem field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        photo_file = request.FILES.get('photo_modem')
        if not photo_file or not photo_file.content_type.startswith('image/'):
            return Response({'error': 'Invalid file type. Only image files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            response = super().partial_update(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        updated_instance = self.get_object()
        if updated_instance.photo_modem != photo_file.name:
            return Response({'error': 'Failed to update photo_modem field.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response


class CreateInternetView(generics.CreateAPIView):
    queryset = Internet.objects.all()
    serializer_class = CreateInternetSerializer


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
        user_email = user.email
        user_first_name = user.first_name or ''
        user_last_name = user.last_name or ''

        if user_first_name and user_last_name:
            user_display = f'{user_first_name} {user_last_name} ({user_email})'
        elif user_first_name or user_last_name:
            user_display = f'{user_first_name}{user_last_name} ({user_email})'
        else:
            user_display = user_email

        if task_instance.status == 'inprogress':
            message = f' {user_display} istifadəçi {task_instance.full_name} adlı müştərinin tapşırığını qəbul etdi.'
        elif task_instance.status == 'started':
            message = f' {user_display} istifadəçi {task_instance.full_name} adlı müştərinin tapşırığının icrasına başladı.'
        elif task_instance.status == 'completed':
            message = f' {user_display} istifadəçi {task_instance.full_name} adlı müştərinin tapşırığını uğurla başa vurdu.'
            self.warehouse_item_decrement(task_instance, user)
        else:
            message = f' {user_display} istifadəçi {task_instance.full_name} adlı müştərinin tapşırığında {task_instance.status} statusuna keçid etdi.'

        report = message + \
            f' Qeydiyyat nömrəsi {task_instance.registration_number}!'

        notification = Notification.objects.create(
            task=task_instance,
            message=message,
            user_email=user.email,
            user_first_name=user.first_name,
            user_last_name=user.last_name,
            action=task_instance.status,
            report=report
        )

        users_excluding_texnik_and_plumber = User.objects.all()

        notification.users.set(users_excluding_texnik_and_plumber)

        notification.save()

    def warehouse_item_decrement(self, task_instance, user):
        warehouse_changes = task_instance.task_items.all()

        for change in warehouse_changes:
            current_count = change.item.count
            new_count = max(0, current_count - change.count)
            change.item.count = new_count
            change.item.save()
            if current_count < change.count:
                WarehouseHistory.objects.create(
                    item=change.item,
                    modified_by=user,
                    action='decrement',
                    old_count=current_count,
                    new_count=new_count,
                    task=task_instance,
                    is_tv=change.is_tv,
                    is_internet=change.is_internet,
                    is_voice=change.is_voice,
                    has_problem=True,
                    must_change=change.count
                )
            else:
                WarehouseHistory.objects.create(
                    item=change.item,
                    modified_by=user,
                    action='decrement',
                    old_count=current_count,
                    new_count=new_count,
                    task=task_instance,
                    is_tv=change.is_tv,
                    is_internet=change.is_internet,
                    is_voice=change.is_voice,
                    has_problem=False,
                    must_change=0
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


class InternetPacksViewSet(viewsets.ModelViewSet):
    queryset = Internet_packages.objects.all()
    serializer_class = InternetPackSerializer


class TaskWarehouseListView(generics.ListAPIView):
    queryset = WarehouseChange.objects.all()
    serializer_class = WarehouseChangeSerializer
    filterset_class = TaskWarehouseFilter
    filter_backends = (DjangoFilterBackend,)


class WarehouseChangeBulkCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = WarehouseChangeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskReportAPIView(APIView):
    def get(self, request, *args, **kwargs):
        queryset = Task.objects.all()

        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month:
            queryset = queryset.filter(date__month=month)
        if year:
            queryset = queryset.filter(date__year=year)

        total = queryset.count()
        # TV tasks
        tv_tasks_total = queryset.filter(is_tv=True).count()
        tv_tasks_by_status = queryset.filter(is_tv=True).values(
            'status').annotate(count=Count('id'))

        # Internet tasks
        internet_tasks_total = queryset.filter(is_internet=True).count()
        internet_tasks_by_status = queryset.filter(
            is_internet=True).values('status').annotate(count=Count('id'))

        # Voice tasks
        voice_tasks_total = queryset.filter(is_voice=True).count()
        voice_tasks_by_status = queryset.filter(is_voice=True).values(
            'status').annotate(count=Count('id'))

        # TV and Internet tasks
        tv_and_internet_total = queryset.filter(
            is_tv=True, is_internet=True).count()
        tv_and_internet_by_status = queryset.filter(
            is_tv=True, is_internet=True).values('status').annotate(count=Count('id'))

        # TV and Voice tasks
        tv_and_voice_total = queryset.filter(is_tv=True, is_voice=True).count()
        tv_and_voice_by_status = queryset.filter(
            is_tv=True, is_voice=True).values('status').annotate(count=Count('id'))

        # Internet and Voice tasks
        internet_and_voice_total = queryset.filter(
            is_internet=True, is_voice=True).count()
        internet_and_voice_by_status = queryset.filter(
            is_internet=True, is_voice=True).values('status').annotate(count=Count('id'))

        # Nəticə
        return Response({
            "total": total,
            "tv_tasks": {
                "total": tv_tasks_total,
                "by_status": list(tv_tasks_by_status),
            },
            "internet_tasks": {
                "total": internet_tasks_total,
                "by_status": list(internet_tasks_by_status),
            },
            "voice_tasks": {
                "total": voice_tasks_total,
                "by_status": list(voice_tasks_by_status),
            },
            "tv_and_internet": {
                "total": tv_and_internet_total,
                "by_status": list(tv_and_internet_by_status),
            },
            "tv_and_voice": {
                "total": tv_and_voice_total,
                "by_status": list(tv_and_voice_by_status),
            },
            "internet_and_voice": {
                "total": internet_and_voice_total,
                "by_status": list(internet_and_voice_by_status),
            },
        })


class MapTaskListView(generics.ListAPIView):
    serializer_class = MapTaskSerializer

    def get_queryset(self):
        email = self.request.query_params.get("email")
        if not email:
            return []
        return Task.objects.filter(
            user__email=email,
            status__in=["inprogress", "started"]
        )
