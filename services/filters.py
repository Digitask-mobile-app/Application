import django_filters
from .models import status_task, TASK_TYPES
from .models import Task
from django_filters import rest_framework as filters
from django import forms
from django_filters import DateFilter


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
            if self.request.user.is_technician:
                return queryset.filter(user=self.request.user) | queryset.filter(status='waiting')
        return queryset
    
class TaskFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='date', lookup_expr='gte', widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',
    }))
    end_date = DateFilter(field_name='date', lookup_expr='lte', widget=forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control',
    }))

    class Meta:
        model = Task
        fields = ['start_date', 'end_date']