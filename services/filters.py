import django_filters
from .models import status_task, TASK_TYPES, Task, WarehouseChange
from django_filters import rest_framework as filters
from django import forms
from accounts.models import User
from datetime import datetime
from django.db.models import Min
from django_filters import DateFilter
from rest_framework import serializers

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


class StatusAndTaskFilter(django_filters.FilterSet):
    status = django_filters.MultipleChoiceFilter(
        choices=status_task, field_name='status')
    task_type = django_filters.ChoiceFilter(
        choices=TASK_TYPES, field_name='task_type')
    month = django_filters.ChoiceFilter(
        choices=MONTH_CHOICES, method='filter_by_month', field_name='date')
    year = django_filters.NumberFilter(
        method='filter_by_year', field_name='date')
    group = django_filters.CharFilter(
        field_name='group__region', lookup_expr='icontains')
    registration_number = django_filters.CharFilter(
        field_name='registration_number', lookup_expr='icontains')

    class Meta:
        model = Task
        fields = ['status', 'task_type', 'month',
                  'group', 'registration_number']

    def filter_by_month(self, queryset, name, value):
        return queryset.filter(date__month=value)

    def filter_by_year(self, queryset, name, value):
        return queryset.filter(date__year=value)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user
        if self.request.user.is_authenticated:
            if user.position and user.position.tasks_permission == 'read_write':
                valid_statuses = ['waiting']
                waiting_tasks = queryset.filter(status__in=valid_statuses)
                texnik_tasks = queryset.filter(user=self.request.user)
                combined_queryset = texnik_tasks | waiting_tasks
                combined_queryset = combined_queryset.distinct()
                return combined_queryset
            elif user.position and user.position.user_permission == 'read_only':
                return queryset
            return []
        return []


class TaskFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        field_name='date', lookup_expr='gte', label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(
        field_name='date', lookup_expr='lte', label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Task
        fields = ['start_date', 'end_date']


class UserFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(
        method='filter_by_date', label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = django_filters.DateFilter(
        method='filter_by_date', label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = User
        fields = []

    def filter_by_date(self, queryset, name, value):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        task_ids = Task.objects.all()

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                task_ids = task_ids.filter(date__gte=start_date)
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid start_date format. Use YYYY-MM-DD.")

        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                task_ids = task_ids.filter(date__lte=end_date)
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid end_date format. Use YYYY-MM-DD.")

        task_ids = task_ids.values_list('user_id', flat=True).distinct()

        return queryset.filter(id__in=task_ids)


class TaskWarehouseFilter(django_filters.FilterSet):

    class Meta:
        model = WarehouseChange
        fields = ['task']
