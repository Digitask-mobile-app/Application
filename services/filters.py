import django_filters
from .models import status_task, TASK_TYPES, Task, Item
from django_filters import rest_framework as filters
from django import forms
from accounts.models import User
from django.db.models import Q


MONTH_CHOICES = [
    (1, 'January'),
    (2, 'February'),
    (3, 'March'),
    (4, 'April'),
    (5, 'May'),
    (6, 'June'),
    (7, 'July'),
    (8, 'August'),
    (9, 'September'),
    (10, 'October'),
    (11, 'November'),
    (12, 'December'),
]

class StatusAndTaskFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(choices=status_task, field_name='status')
    task_type = django_filters.ChoiceFilter(choices=TASK_TYPES, field_name='task_type')
    month = django_filters.ChoiceFilter(choices=MONTH_CHOICES, method='filter_by_month', field_name='date')

    class Meta:
        model = Task
        fields = ['status', 'task_type', 'month']

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(date__month=value)
    
    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        
        if self.request.user.is_authenticated:
            if self.request.user.is_texnik:
                valid_statuses = ['waiting']  
                texnik_tasks = queryset.filter(user=self.request.user)
                waiting_tasks = queryset.filter(status__in=valid_statuses)
                
                combined_queryset = texnik_tasks | waiting_tasks
                combined_queryset = combined_queryset.distinct()
                
                return combined_queryset
            
        return queryset

    

class TaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name='date', lookup_expr='gte', label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(field_name='date', lookup_expr='lte', label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Task
        fields = ['start_date', 'end_date']

class UserFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(method='filter_by_date', label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(method='filter_by_date', label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = []

    def filter_by_date(self, queryset, name, value):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if start_date and end_date:
            tasks = Task.objects.filter(
                Q(date__gte=start_date) & Q(date__lte=end_date)
            )
            task_user_ids = tasks.values_list('user_id', flat=True).distinct()

            return queryset.filter(
                Q(id__in=task_user_ids) | Q(task__isnull=True)
            ).distinct()
        
        return queryset


class WarehouseItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='equipment_name', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['name']
