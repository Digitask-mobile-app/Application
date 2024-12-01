from django.db import models
from accounts.models import User, Group
# from django.contrib.gis.db import models
from django.utils import timezone



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
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class Task(Status):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True,related_name="user_tasks")
    full_name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=100, choices=TASK_TYPES)
    registration_number = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100)
    passport = models.ImageField(null=True,blank=True)
    note = models.TextField(null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    group = models.ManyToManyField(
        Group, related_name='group_tasks', blank=True)
    status = models.CharField(
        max_length=100, choices=status_task, default='waiting')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_voice = models.BooleanField(default=False)
    is_internet = models.BooleanField(default=False)
    is_tv = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.task_type

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
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='internet')
    photo_modem = models.ImageField(
        upload_to='internet/', null=True, blank=True)
    modem_SN = models.CharField(max_length=100, null=True, blank=True)
    # optical_cable = models.CharField(max_length=100, null=True, blank=True)
    # fastconnector = models.CharField(max_length=100, null=True, blank=True)
    siqnal = models.CharField(max_length=100, null=True, blank=True)
    internet_packs = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.task.registration_number

class TV(models.Model):
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='tv')
    photo_modem = models.ImageField(upload_to='tv/', null=True, blank=True)
    modem_SN = models.CharField(max_length=100, null=True, blank=True)
    # rg6_cable = models.CharField(max_length=100, null=True, blank=True)
    # f_connector = models.CharField(max_length=100, null=True, blank=True)
    # splitter = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.task.registration_number

class Voice(models.Model):
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='voice')
    photo_modem = models.ImageField(upload_to='voice/', null=True, blank=True)
    modem_SN = models.CharField(max_length=100, null=True, blank=True)
    home_number = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.task.registration_number
    

class WarehouseChange(models.Model):
    from warehouse.models import Item
    task = models.ForeignKey(Task,on_delete=models.CASCADE,related_name='task_items')
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name='item_tasks')
    count = models.PositiveIntegerField()
    delivery_note = models.TextField(blank=True, null=True, default="qeyd yoxdur")
    is_tv = models.BooleanField(default=False)
    is_internet = models.BooleanField(default=False)
    is_voice = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.task.user:
            self.delivery_note = f"{self.task.user.first_name} {self.task.user.last_name} tapsirig icrasinda - {self.item.equipment_name} mehsulundan {self.count} qeder istifade edildi"
        super().save(*args, **kwargs)
    


class PlumberTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    count = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.equipment



