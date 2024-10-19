from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet,ItemViewSet, WarehouseHistoryListView

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet)  
router.register(r'warehouse-items', ItemViewSet)  

urlpatterns = [
    path('', include(router.urls)),  
    path('warehouse-history/', WarehouseHistoryListView.as_view(), name='warehouse-history-list'),
]