import django_filters
from .models import status_task, TASK_TYPES, Task, Item
from django_filters import rest_framework as filters
from django import forms
from accounts.models import User
import datetime

MONTH_CHOICES = [
    (1, 'Yanvar'),
    (2, 'Fevral'),
    (3, 'Mart'),
    (4, 'Aprel'),
    (5, 'May'),
    (6, 'İyun'),
    (7, 'İyul'),
    (8, 'Avqust'),
    (9, 'Sentyabr'),
    (10, 'Oktyabr'),
    (11, 'Noyabr'),
    (12, 'Dekabr'),
]

from django.db.models import Min, Max

def get_year_choices():
    years = Task.objects.aggregate(
        min_year=Min('date__year'),
        max_year=Max('date__year')
    )
    min_year = years['min_year']
    max_year = years['max_year']
    if min_year and max_year:
        return [(year, str(year)) for year in range(min_year, max_year + 1)]
    else:
        current_year = datetime.now().year
        return [(current_year, str(current_year))]


class StatusAndTaskFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(choices=status_task, field_name='status')
    task_type = django_filters.ChoiceFilter(choices=TASK_TYPES, field_name='task_type')
    month = django_filters.ChoiceFilter(choices=MONTH_CHOICES, method='filter_by_month', field_name='date')
    year = django_filters.ChoiceFilter(choices=get_year_choices(), method='filter_by_year', field_name='year')

    class Meta:
        model = Task
        fields = ['status', 'task_type', 'month', 'year']

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(date__month=value)
    
    def filter_by_year(self, queryset, name, value):
        return queryset.filter(date__year=value)
    
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

        task_ids = Task.objects.filter(date__gte=start_date, date__lte=end_date).values_list('user_id', flat=True).distinct()

        if start_date and end_date:
            return queryset.filter(id__in=task_ids)
        elif start_date:
            return queryset.filter(id__in=task_ids)
        elif end_date:
            return queryset.filter(id__in=task_ids)
        return queryset



class WarehouseItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='equipment_name', lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['name']
