from django.shortcuts import render
from rest_framework import viewsets
from .models import Warehouse, Item, WarehouseHistory
from .serializers import WarehouseUserSerializer, WarehouseSerializer, ItemSerializer, WarehouseHistorySerializer
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .filters import WarehouseHistoryFilter


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.filter()
    serializer_class = WarehouseSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            warehouse = self.get_object()
            warehouse.is_deleted = True
            warehouse.save()

            return Response({'message': f'{warehouse.name} warehouse has been deleted.'}, status=status.HTTP_204_NO_CONTENT)

        except Warehouse.DoesNotExist:
            return Response({'error': 'Warehouse not found.'}, status=status.HTTP_404_NOT_FOUND)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.filter(is_deleted=False)
    serializer_class = ItemSerializer

    def get_queryset(self):
        queryset = Item.objects.filter(is_deleted=False, count__gt=0)
        warehouse_id = self.request.query_params.get('warehouse')
        name = self.request.query_params.get('name')
        region = self.request.query_params.get('region')
        if name:
            queryset = queryset.filter(equipment_name__icontains=name)
        if warehouse_id:
            queryset = queryset.filter(warehouse=warehouse_id)
        if region:
            queryset = queryset.filter(warehouse__region=region)

        return queryset

    def create(self, request, *args, **kwargs):
        item_data = request.data.copy()
        item_data['created_by'] = request.user.id

        serializer = self.get_serializer(data=item_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        WarehouseHistory.objects.create(
            item=serializer.instance,
            modified_by=request.user,
            action='add',
            old_count=serializer.instance.count,
            new_count=serializer.instance.count,
            delivery_note=request.data.get('delivery_note', ''),
            requested_count=request.data.get(
                'requested_count', serializer.instance.count),

        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        item = self.get_object()
        old_count = item.count
        response = super().update(request, *args, **kwargs)

        item.refresh_from_db()

        WarehouseHistory.objects.create(
            item=item,
            modified_by=request.user,
            action='increment' if item.count > old_count else 'decrement',
            old_count=old_count,
            new_count=item.count,
            delivery_note=request.data.get('delivery_note', ''),
            requested_count=request.data.get('requested_count'),
        )

        return response

    def destroy(self, request, *args, **kwargs):
        try:
            item = self.get_object()
            old_count = item.count
            requested_count = int(request.data.get('requested_count', 0))
            has_problem = requested_count > old_count
            item.count = 0
            item.is_deleted = True
            item.save()

            WarehouseHistory.objects.create(
                item=item,
                modified_by=request.user,
                action='remove',
                old_count=old_count,
                new_count=0,
                delivery_note=request.data.get('delivery_note', ''),
                requested_count=requested_count,
            )

            return Response({'message': f'Item has been deleted and count set to zero.'}, status=status.HTTP_204_NO_CONTENT)

        except Warehouse.DoesNotExist:
            return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)


class WarehouseHistoryListView(generics.ListAPIView):
    queryset = WarehouseHistory.objects.all()
    serializer_class = WarehouseHistorySerializer
    filterset_class = WarehouseHistoryFilter
