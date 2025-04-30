from .models import Warehouse, Item, WarehouseHistory
from rest_framework import serializers
from django.conf import settings
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL)


class WarehouseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


class WarehouseSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'region', 'region_name', 'is_deleted']


class ItemSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['created_by_name']

    def get_created_by_name(self, obj):
        user = obj.created_by
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name if full_name else user.email


class WarehouseHistorySerializer(serializers.ModelSerializer):
    modified_by = WarehouseUserSerializer(read_only=True)
    item = ItemSerializer()

    class Meta:
        model = WarehouseHistory
        fields = '__all__'
