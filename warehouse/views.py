from django.shortcuts import render
from rest_framework import viewsets
from models import Warehouse, Item, WarehouseHistory
from serializers import WarehouseUserSerializer, WarehouseSerializer, ItemSerializer, WarehouseHistorySerializer
from django.conf import settings

class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()  
    serializer_class = WarehouseSerializer