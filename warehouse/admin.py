from django.contrib import admin
from .models import Warehouse, Item, WarehouseHistory

admin.site.register(Warehouse)
admin.site.register(Item)
admin.site.register(WarehouseHistory)
