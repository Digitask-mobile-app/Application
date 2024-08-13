from .models import Task, Item, History
from .serializers import *
from .filters import StatusAndTaskFilter, WarehouseItemFilter, HistoryFilter, IncrementHistoryFilter
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


class CreateTaskView(generics.CreateAPIView):
    serializer_class = TaskDetailSerializer


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


# @receiver(pre_delete, sender=Item)
# def warehouse_pre_delete(sender, instance, **kwargs):
#     History.objects.create(
#         item=instance,
#         action='export'
#     )

class ItemImportView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise ValueError("İstifadəçinin autentifikasiyası yoxdur.")
        serializer.save(created_by=self.request.user)


class ItemListView(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = WarehouseItemSerializer
    filterset_class = WarehouseItemFilter
    filter_backends = (DjangoFilterBackend,)


class WarehouseListView(ListAPIView):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer


class DecrementItemView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DecrementItemSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data['item_id']
        company = serializer.validated_data['company']
        authorized_person = serializer.validated_data['authorized_person']
        number = serializer.validated_data['number']
        texnik_user = serializer.validated_data['texnik_user']

        try:
            item = Item.objects.get(id=item_id)
            item.decrement(number, company, authorized_person,
                           request.user, texnik_user)

            # latest_history = History.objects.filter(item=item).order_by('-date').first()
            # history_serializer = HistorySerializer(latest_history)
            user_serializer = UserSerializer(request.user)

            return Response({
                "message": "Element uğurla azaldıldı.",
                "request_user": user_serializer.data,
                # "history": history_serializer.data
            }, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({"error": "Element tapılmadı."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class IncrementItemView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = IncrementItemSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_id = serializer.validated_data['item_id']
        product_provider = serializer.validated_data['product_provider']
        number = serializer.validated_data['number']

        try:
            item = Item.objects.get(id=item_id)
            item.increment(number, product_provider, request.user)

            return Response({
                "message": "Element uğurla artırıldı."
            }, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({"error": "Element tapılmadı."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TexnikUserListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='Texnik')
    serializer_class = ItemUserSerializer
    permission_classes = [IsAuthenticated]


class HistoryListView(generics.ListAPIView):
    queryset = History.objects.all().order_by('-date')
    serializer_class = HistorySerializer
    filterset_class = HistoryFilter
    filter_backends = [DjangoFilterBackend]


class HistoryIncrementListView(generics.ListAPIView):
    queryset = HistoryIncrement.objects.all().order_by('-date')
    serializer_class = HistoryIncrementSerializer
    filterset_class = IncrementHistoryFilter
    filter_backends = [DjangoFilterBackend]


class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
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
    serializer_class = TaskUpdateSerializer
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
        user_email = self.request.user.email

        if instance.status == 'inprogress':
            message = f' istifadəçi {instance.full_name} adlı müştərinin tapşırığını qəbul etdi.'
        elif instance.status == 'started':
            message = f' istifadəçi {instance.full_name} adlı müştərinin tapşırığının icrasına başladı.'
        elif instance.status == 'completed':
            message = f' istifadəçi {instance.full_name} adlı müştərinin tapşırığını uğurla başa vurdu.'
        else:
            message = f' istifadəçi {instance.full_name} adlı müştərinin tapşırığında {instance.status} statusuna keçid etdi.'
        print('ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc')
        notification = Notification.objects.create(
            message=message, user_email=user_email)
        texnik_users = User.objects.filter(user_type='Ofis menecer')
        plumber_users = User.objects.filter(user_type='Texnik menecer')
        notification.users.set(texnik_users | plumber_users)
        notification.save()


class MeetingsApiView(generics.ListAPIView):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

# @csrf_exempt
# def export_item(request, id):
#     if request.method == 'DELETE':
#         try:
#             warehouse_item = Warehouse.objects.get(id=id)
#             History.objects.create(
#                 warehouse_item=warehouse_item,
#                 action='export'
#             )
#             warehouse_item.delete()
#             return JsonResponse({"success": "Item exported successfully."})
#         except Warehouse.DoesNotExist:
#             return JsonResponse({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         return JsonResponse({"error": "Invalid request method."}, status=status.HTTP_400_BAD_REQUEST)
