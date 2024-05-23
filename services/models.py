from django.db import models, transaction
from accounts.models import User,Group
# from django.contrib.gis.db import models
from django.db.models import ProtectedError
from django.db.models.signals import post_delete
from django.dispatch import receiver

TASK_TYPES = (
    ('connection', 'connection'),
    ('problem', 'problem'),
)

status_task = (
    ("waiting", 'waiting'),
    ("inprogress", "inprogress"),
    ("started", "started"),
    ("completed", "completed"),
)

class Status(models.Model):
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        abstract = True


class Task(Status):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    task_type = models.CharField(max_length=100, choices=TASK_TYPES)
    description = models.TextField(null=True,blank=True)
    registration_number = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100,null=True,blank=True)
    location = models.CharField(max_length=100)  
    note = models.TextField(null=True,blank=True)
    date = models.DateField()
    group = models.ManyToManyField(Group, related_name='group_tasks',blank=True)
    status = models.CharField(max_length=100, choices=status_task, default='waiting')

    is_voice = models.BooleanField(default=False)
    is_internet = models.BooleanField(default=False)
    is_tv = models.BooleanField(default=False)

    def __str__(self):
        return self.description
 

    def is_service(self):
        return hasattr(self, 'internet') or hasattr(self, 'tv') or hasattr(self, 'voice')

    def get_service(self):
        if hasattr(self, 'internet') and self.internet:
            return 'Internet'
        if hasattr(self, 'tv') and self.tv:
            return 'TV'
        if hasattr(self, 'voice') and self.voice:
            return 'Voice'
        return None
    
    

class Internet(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='internet')
    photo_modem = models.ImageField(upload_to='internet/')
    modem_SN = models.CharField(max_length=100)
    optical_cable = models.CharField(max_length=100)
    fastconnector = models.CharField(max_length=100)
    siqnal = models.CharField(max_length=100)


class TV(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='tv')
    photo_modem = models.ImageField(upload_to='tv/')
    modem_SN = models.CharField(max_length=100)
    rg6_cable = models.CharField(max_length=100)
    f_connector = models.CharField(max_length=100)
    splitter = models.CharField(max_length=100)


class Voice(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name='voice')
    photo_modem = models.ImageField(upload_to='voice/')
    modem_SN = models.CharField(max_length=100)
    home_number = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class PlumberTask(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    equipment = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    count =  models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.equipment

class WarehouseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)
    
class Warehouse(models.Model):
    equipment_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=True)
    number = models.PositiveIntegerField()
    region = models.CharField(max_length=255)
    size_length = models.DecimalField(max_digits=10, decimal_places=2)
    deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.equipment_name} - {self.serial_number}"
    
    objects = WarehouseManager()

    def delete(self):
        self.deleted = True
        self.save()


class History(models.Model):
    ACTION_CHOICES = [
        ('import', 'Import'),
        ('export', 'Export')
    ]
    warehouse_item = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.warehouse_item:
            return f"{self.get_action_display()} - {self.warehouse_item.equipment_name} - {self.timestamp}"
        else:
            return f"{self.get_action_display()} - Deleted Warehouse Item - {self.timestamp}"


