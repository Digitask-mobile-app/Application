import django_filters
from .models import WarehouseHistory

class WarehouseHistoryFilter(django_filters.FilterSet):
    
    class Meta:
        model = WarehouseHistory
        fields = {
            'item': ['exact'],  
            'modified_by': ['exact'],
            'action': ['exact'], 
            'timestamp': ['date__gte', 'date__lte'], 
        }