from django.db import models
from accounts.models import User, Group
# from django.contrib.gis.db import models
from django.utils import timezone
from django.conf import settings
from datetime import datetime

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
        User, on_delete=models.SET_NULL, blank=True, null=True)
    full_name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=100, choices=TASK_TYPES)
    registration_number = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100)
    note = models.TextField(null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    group = models.ManyToManyField(
        Group, related_name='group_tasks', blank=True)
    status = models.CharField(
        max_length=100, choices=status_task, default='waiting')

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
    optical_cable = models.CharField(max_length=100, null=True, blank=True)
    fastconnector = models.CharField(max_length=100, null=True, blank=True)
    siqnal = models.CharField(max_length=100, null=True, blank=True)


class TV(models.Model):
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='tv')
    photo_modem = models.ImageField(upload_to='tv/', null=True, blank=True)
    modem_SN = models.CharField(max_length=100, null=True, blank=True)
    rg6_cable = models.CharField(max_length=100, null=True, blank=True)
    f_connector = models.CharField(max_length=100, null=True, blank=True)
    splitter = models.CharField(max_length=100, null=True, blank=True)


class Voice(models.Model):
    task = models.OneToOneField(
        Task, on_delete=models.CASCADE, related_name='voice')
    photo_modem = models.ImageField(upload_to='voice/', null=True, blank=True)
    modem_SN = models.CharField(max_length=100, null=True, blank=True)
    home_number = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)


class PlumberTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipment = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    count = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return self.equipment


class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class Item(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    equipment_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    mac = models.CharField(max_length=255, blank=True, null=True)
    port_number = models.PositiveIntegerField(blank=True, null=True)
    serial_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    number = models.PositiveIntegerField()
    size_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.equipment_name} - {self.serial_number}"

    objects = ItemManager()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            full_name = f"{self.created_by.first_name} {self.created_by.last_name}"
            HistoryIncrement.objects.create(
                item_warehouse=self.warehouse,
                item_equipment_name=self.equipment_name,
                item_brand=self.brand,
                item_model=self.model,
                item_mac=self.mac,
                item_port_number=self.port_number,
                item_serial_number=self.serial_number,
                item_size_length=self.size_length,
                product_provider=full_name,
                number=self.number,
                date=self.date,
                item_created_by=self.created_by
            )

    def decrement(self, number, company, authorized_person, user, texnik_user):
        if self.number >= number:
            self.number -= number
            if self.number == 0:
                self.delete()
            else:
                self.save()

            History.objects.create(
                item_warehouse=self.warehouse,
                item_equipment_name=self.equipment_name,
                item_brand=self.brand,
                item_model=self.model,
                item_mac=self.mac,
                item_port_number=self.port_number,
                item_serial_number=self.serial_number,
                item_size_length=self.size_length,
                company=company,
                authorized_person=authorized_person,
                number=number,
                texnik_user=texnik_user,
                item_created_by=user
            )
        else:
            raise ValueError("Azaltmaq üçün kifayət qədər element yoxdur")

    def increment(self, number, product_provider, user):
        self.number += number
        self.save()

        HistoryIncrement.objects.create(
            item_warehouse=self.warehouse,
            item_equipment_name=self.equipment_name,
            item_brand=self.brand,
            item_model=self.model,
            item_mac=self.mac,
            item_port_number=self.port_number,
            item_serial_number=self.serial_number,
            item_size_length=self.size_length,
            product_provider=product_provider,
            number=number,
            item_created_by=user
        )


class History(models.Model):
    item_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    item_equipment_name = models.CharField(max_length=255)
    item_brand = models.CharField(max_length=255)
    item_model = models.CharField(max_length=255)
    item_mac = models.CharField(max_length=255)
    item_port_number = models.PositiveIntegerField()
    item_serial_number = models.CharField(max_length=255)
    item_size_length = models.DecimalField(max_digits=10, decimal_places=2)
    company = models.CharField(max_length=255, blank=True, null=True)
    authorized_person = models.CharField(max_length=255, blank=True, null=True)
    number = models.PositiveIntegerField()
    texnik_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='texnik_actions', blank=True, null=True)
    date = models.DateTimeField(default=datetime.now)
    item_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_items')

    def __str__(self):
        return f"{self.item_equipment_name}"


class HistoryIncrement(models.Model):
    item_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    item_equipment_name = models.CharField(max_length=255)
    item_brand = models.CharField(max_length=255)
    item_model = models.CharField(max_length=255)
    item_mac = models.CharField(max_length=255)
    item_port_number = models.PositiveIntegerField()
    item_serial_number = models.CharField(max_length=255)
    item_size_length = models.DecimalField(max_digits=10, decimal_places=2)
    product_provider = models.CharField(max_length=255, blank=True, null=True)
    number = models.PositiveIntegerField()
    date = models.DateTimeField(default=datetime.now)
    item_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_increment_items')

    def __str__(self):
        return f"{self.item_equipment_name} - {self.item_serial_number} - artırıldı"
