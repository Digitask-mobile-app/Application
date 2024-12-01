from django_filters import rest_framework as filters
from .models import User,USER_TYPE,Message

class UserFilter(filters.FilterSet):
    user_type = filters.CharFilter(field_name="user_type", lookup_expr="exact")
    group = filters.CharFilter(field_name="group__group", lookup_expr="exact")

    class Meta:
        model = User
        fields = ['user_type', 'group']

class UserTypeFilter(filters.FilterSet):
    user_type = filters.ChoiceFilter(choices=USER_TYPE)
    group = filters.CharFilter(field_name="group__group", lookup_expr="exact")

    class Meta:
        model = User
        fields = ['user_type', 'group']


class MessageFilter(filters.FilterSet):
    room = filters.NumberFilter(field_name='room__id')

    class Meta:
        model = Message
        fields = ['room']


class MessagesFilter(filters.FilterSet):
    room = filters.NumberFilter(field_name='room__id')

    class Meta:
        model = Message
        fields = ['room']



from .models import Notification


class NotificationFilter(filters.FilterSet):
    date = filters.DateFilter(field_name='created_at', lookup_expr='exact', label='Exact Date')
    month = filters.CharFilter(field_name='created_at', method='filter_by_month', label='Month (YYYY-MM)')

    class Meta:
        model = Notification
        fields = ['date', 'month']

    def filter_by_month(self, queryset, name, value):
        # Ay ve yıl formatında filtreleme yapar (YYYY-MM)
        try:
            year, month = value.split('-')
            return queryset.filter(created_at__year=year, created_at__month=month)
        except ValueError:
            return queryset.none()