import django_filters
from .models import status_task, TASK_TYPES
from .models import Task

class StatusAndTaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=status_task, field_name='status')
    task_type = django_filters.ChoiceFilter(choices=TASK_TYPES, field_name='task_type')
    class Meta:
        model = Task
        fields = ['status', 'task_type']

