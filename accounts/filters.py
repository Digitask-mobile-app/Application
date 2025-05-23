from django_filters import rest_framework as filters, DateFilter
from .models import User,Position,Message

class UserFilter(filters.FilterSet):
    position = filters.CharFilter(field_name="position__name", lookup_expr="exact")
    group = filters.CharFilter(field_name="group__group", lookup_expr="exact")

    class Meta:
        model = User
        fields = ['position', 'group']

class UserTypeFilter(filters.FilterSet):
    position = filters.CharFilter(field_name="position__name", lookup_expr="exact")
    group = filters.CharFilter(field_name="group__group", lookup_expr="exact")

    class Meta:
        model = User
        fields = ['position', 'group']


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


class CustomDateFilter(DateFilter):
    def filter(self, qs, value):
        if value:
            filter_lookups = {
                f"{self.field_name}__month": value.month,
                f"{self.field_name}__year": value.year,
            }
            qs = qs.filter(**filter_lookups)
        return qs

class NotificationFilter(filters.FilterSet):
    created_at_month = filters.NumberFilter(field_name='created_at__month', lookup_expr='exact')
    created_at_year = filters.NumberFilter(field_name='created_at__year', lookup_expr='exact')

    class Meta:
        model = Notification
        fields = ['created_at_month', 'created_at_year']