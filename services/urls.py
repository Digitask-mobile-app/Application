from django.urls import path,include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'warehouse_change', views.WarehouseChangeViewSet)  


urlpatterns = [
    path('warehouse/', include(router.urls)),   


    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('usertasks/', views.UserTaskListView.as_view(), name='user_tasks'),
    path('task/<int:id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('status/', views.TaskListAPIView.as_view(), name='filtered_tasks'),
    path('performance/', views.PerformanceListView.as_view(), name='performance'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path("create_employee_group", views.CreateGroupView.as_view(),
         name="create_employee_group"),
    path('update_task/<int:pk>/',
         views.TaskUpdateAPIView.as_view(), name='update_task'),
     path('update_task_image/<int:pk>/',
         views.TaskImageUpdateAPIView.as_view(), name='update_task'),
    path('create_meeting/', views.CreateMeetingView.as_view(), name='create_meeting'),
    path('task/<int:id>/delete/',
         views.TaskDeleteAPIView.as_view(), name='task-delete'),
    path('create_task/', views.CreateTaskView.as_view(), name='create_task'),
    path('create_tv/', views.CreateTvView.as_view(), name='creat_tv'),
    path('update_tv/<int:pk>/', views.UpdateTvView.as_view(), name='update_tv'),
    path('create_internet/', views.CreateInternetView.as_view(),
         name='creat_internet'),
    path('update_internet/<int:pk>/',
         views.UpdateInternetView.as_view(), name='update_internet'),
    path('create_voice/', views.CreateVoiceView.as_view(), name='creat_voice'),
    path('update_voice/<int:pk>/',
         views.UpdateVoiceView.as_view(), name='update_voice'),
    path('mainpage/', views.MainPageView.as_view(), name='mainpage'),
    path('task/<int:pk>/update/', views.UpdateTaskView.as_view(), name='update-task'),
    path('meetings/', views.MeetingsApiView.as_view(), name='meetings'),
    path('meeting/<int:id>/', views.MeetingDetailView.as_view(),
         name='meeting-detail'),
    path('healthcheck/', views.health_check),
    path('TaskWarehouseListView/', views.TaskWarehouseListView.as_view(), name='TaskWarehouseListView'),
    path('warehouse_changes/bulk_create/', views.WarehouseChangeBulkCreateView.as_view(), name='warehousechange-bulk-create'),
]
# s