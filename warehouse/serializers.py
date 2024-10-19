from .models import Warehouse, Item, WarehouseHistory
from rest_framework import serializers
from django.conf import settings
from django.apps import apps

User = apps.get_model(settings.AUTH_USER_MODEL)

class WarehouseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','email']

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class WarehouseHistorySerializer(serializers.ModelSerializer):
    modified_by = WarehouseUserSerializer(read_only=True)

    class Meta:
        model = WarehouseHistory
        fields = '__all__'