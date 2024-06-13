from django.urls import path
from . import views

urlpatterns = [
    
    path('tasks/', views.TaskListView.as_view(), name='tasks'),
    path('usertasks/', views.UserTaskListView.as_view(), name='user_tasks'),
    path('task/<int:id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('status/', views.TaskListAPIView.as_view(), name='filtered_tasks'),
    path('performance/', views.PerformanceListView.as_view(), name='performance'),
    path('warehouse_item/', views.ItemListView.as_view(), name='warehouse-item'),
    path('history/', views.HistoryListView.as_view(), name='history_list'),
    path('import/', views.ItemImportView.as_view(), name='warehouse-item-import'),
    path('export/<int:id>/', views.ItemExportView.as_view(), name='warehouse-item-export'),
    path('groups/', views.GroupListView.as_view(), name='tasks'),
    path('update_task/<int:pk>/', views.TaskUpdateAPIView.as_view(), name='update_task'),
    path('create_meeting/', views.CreateMeetingView.as_view(), name='create_meeting'),
    path('task/<int:id>/delete/', views.TaskDeleteAPIView.as_view(), name='task-delete'),


    path('create_task/', views.CreateTaskView.as_view(), name='create_task'),
    path('creat_tv/', views.CreateUpdateTvView.as_view(), name='creat_tv'),
    path('update_tv/<int:pk>/', views.CreateUpdateTvView.as_view(), name='update_tv'),

    path('creat_internet/', views.CreateUpdateInternetView.as_view(), name='creat_internet'),
    path('update_internet/<int:pk>/', views.CreateUpdateInternetView.as_view(), name='update_internet'),

    path('creat_voice/', views.CreateUpdateVoiceView.as_view(), name='creat_voice'),
    path('update_voice/<int:pk>/', views.CreateUpdateVoiceView.as_view(), name='update_voice'),
    path('mainpage/', views.MainPageView.as_view(), name='mainpage'),
    path('task/<int:pk>/update/', views.UpdateTaskView.as_view(), name='update-task'),
]
#