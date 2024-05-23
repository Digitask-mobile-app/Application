from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Warehouse, History

class WarehouseTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.warehouse_data = {
            "equipment_name": "Excavator",
            "brand": "Caterpillar",
            "model": "320D",
            "serial_number": "CAT0320D",
            "number": 5,
            "region": "Central",
            "size_length": 20.5
        }
        self.warehouse_url = reverse('warehouse-import')

    def test_import_warehouse_item(self):
        response = self.client.post(self.warehouse_url, self.warehouse_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Warehouse.objects.count(), 1)
        self.assertEqual(History.objects.count(), 1)

    def test_export_warehouse_item(self):
        self.client.post(self.warehouse_url, self.warehouse_data, format='json')
        warehouse_item = Warehouse.objects.first()
        export_url = reverse('warehouse-export', kwargs={'id': warehouse_item.id})
        response = self.client.delete(export_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Warehouse.objects.count(), 0)
        self.assertEqual(History.objects.count(), 2)

if __name__ == '__main__':
    TestCase.main()
