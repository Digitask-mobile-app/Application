from django_filters import rest_framework as filters, DateFilter
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
    date = CustomDateFilter(field_name='created_at', label='Month and Year (YYYY-MM-DD)')

    class Meta:
        model = Notification
        fields = ['date']