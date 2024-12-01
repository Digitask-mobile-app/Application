from django.db import models
from django.conf import settings

class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Item(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    equipment_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    mac = models.CharField(max_length=255, blank=True, null=True)
    port_number = models.PositiveIntegerField(blank=True, null=True)
    serial_number = models.CharField(
        max_length=255,  blank=True, null=True)
    size_length = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    
    date = models.DateField(auto_now_add=True)
    created_by = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE )

    is_deleted = models.BooleanField(default=False)
    count = models.PositiveIntegerField()

    def __str__(self):
        return self.equipment_name

    class Meta:
        ordering = ['equipment_name']
    
    
class WarehouseHistory(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add Item'),        
        ('remove', 'Remove Item'),   
        ('increment', 'Increment'),  
        ('decrement', 'Decrement'),  
    ]

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='history')
    modified_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    old_count = models.PositiveIntegerField(null=True, blank=True)  
    new_count = models.PositiveIntegerField(null=True, blank=True)  
    
    delivery_note = models.TextField(null=True,blank=True,default="Qeyd yoxdur")

    task = models.ForeignKey('services.Task',on_delete=models.CASCADE,null=True,blank=True)
    is_tv = models.BooleanField(default=False)
    is_internet = models.BooleanField(default=False)
    is_voice = models.BooleanField(default=False)

    has_problem = models.BooleanField(default=False)
    must_change = models.PositiveBigIntegerField(default=0, null=True,blank=True)

    def __str__(self):
        return f"{self.item.equipment_name}  - {self.action}"
    

