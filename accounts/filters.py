from django_filters import rest_framework as filters
from .models import User,USER_TYPE

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