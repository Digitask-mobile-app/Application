from .models import Task, Item, History
from .serializers import *
from .filters import StatusAndTaskFilter,TaskFilter
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
    filterset_class = TaskFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return User.objects.filter(task__isnull=False).distinct()



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
            warehouse_item.number += 1
            warehouse_item.save()
        return response

class ItemListView(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = WarehouseItemSerializer

class ItemExportView(generics.DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = WarehouseItemSerializer
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            with transaction.atomic():
                deleted_instance = instance
                History.objects.create(
                    warehouse_item=deleted_instance,
                    action='export'
                )
                warehouse_item = Item.objects.get(id=instance.id)
                warehouse_item.number -= 1
                warehouse_item.save()
                instance.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class HistoryListView(APIView):
    def get(self, request):
        history_items = History.objects.all()
        serializer = HistorySerializer(history_items, many=True)
        return Response(serializer.data)
    
class TaskUpdateAPIView(generics.UpdateAPIView):
    queryset = Task.objects.all()
    serializer_class = CreateTaskSerializer

class CreateMeetingView(generics.CreateAPIView):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()  

#####################################################################################################################


class MainPageView(generics.RetrieveAPIView):
    serializer_class = MainPageUserSerializer

    def get_object(self):
        return self.request.user

class CreateTaskView(generics.CreateAPIView):
    serializer_class = CreateTaskSerializer
    queryset = Task.objects.all()


class CreateUpdateTvView(generics.CreateAPIView,generics.UpdateAPIView):
    serializer_class = TVSerializer
    queryset = TV.objects.all()

class CreateUpdateInternetView(generics.CreateAPIView,generics.UpdateAPIView):
    serializer_class = InternetSerializer
    queryset = Internet.objects.all()

class CreateUpdateVoiceView(generics.CreateAPIView,generics.UpdateAPIView):
    serializer_class = VoiceSerializer
    queryset = Voice.objects.all()
   
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