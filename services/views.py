from .models import Task, Item, History
from .serializers import *
from .filters import StatusAndTaskFilter,UserFilter, WarehouseItemFilter
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from accounts.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.views import View
from django.db.models import Subquery, OuterRef
from accounts.serializers import UserSerializer

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
    filterset_class = UserFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        users = User.objects.all()

        user_filter = UserFilter(self.request.GET, queryset=users, request=self.request)
        filtered_users = user_filter.qs

        return filtered_users



@receiver(pre_delete, sender=Item)
def warehouse_pre_delete(sender, instance, **kwargs):
    History.objects.create(
        warehouse_item=instance,
        action='export'
    )
    
class ItemImportView(generics.CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            warehouse_item = Item.objects.get(id=response.data['id'])
            warehouse_item.save()
        return response

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
        date = serializer.validated_data['date']
        
        try:
            item = Item.objects.get(id=item_id)
            item.decrement(number, company, authorized_person, request.user, texnik_user, date)

            latest_history = History.objects.filter(item=item).order_by('-date').first()
            history_serializer = HistorySerializer(latest_history)
            user_serializer = UserSerializer(request.user) 

            return Response({
                "message": "Element uğurla azaldıldı.",
                "request_user": user_serializer.data, 
                "history": history_serializer.data
            }, status=status.HTTP_200_OK)

        except Item.DoesNotExist:
            return Response({"error": "Element tapılmadı."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
class TexnikUserListView(generics.ListAPIView):
    queryset = User.objects.filter(user_type='Texnik')
    serializer_class = TexnikUserSerializer
    permission_classes = [IsAuthenticated]

class HistoryListView(APIView):
    def get(self, request):
        history_items = History.objects.all()
        serializer = HistorySerializer(history_items, many=True)
        return Response(serializer.data)
    
class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = UpdateTaskSerializer
    http_method_names = ['patch']

class CreateMeetingView(generics.CreateAPIView):
    serializer_class = CreatingMeetingSerializer
    queryset = Meeting.objects.all()  

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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


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