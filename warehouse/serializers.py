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
    class Meta:
        model = Item
        fields = '__all__'


class WarehouseHistorySerializer(serializers.ModelSerializer):
    modified_by = WarehouseUserSerializer(read_only=True)
    item = ItemSerializer()

    class Meta:
        model = WarehouseHistory
        fields = '__all__'
