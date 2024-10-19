from models import Warehouse, Item, WarehouseHistory
from rest_framework import serializers
from django.conf import settings

class WarehouseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
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
    created_by = WarehouseUserSerializer()

    class Meta:
        model = WarehouseHistory
        fields = '__all__'