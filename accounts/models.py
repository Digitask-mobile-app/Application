from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import validate_phone_number


MEETING_TYPES = (
    ('Şənlik', 'Şənlik'),
    ('Toplantı', 'Toplantı'),
    ('Konfrans', 'Konfrans'),
    ('Seminar', 'Seminar'),
)

AUTH_PROVIDERS = {'email': 'email'}

USER_PERMISSIONS = (
    ('no_access', 'no_access'),
    ('read_only', 'read_only'),
    ('read_write', 'read_write'),
    ('is_admin', 'is_admin')
)

TASK_PERMISSIONS = (
    ('technician', 'technician'),
    ('read_write', 'read_write'),
    ('is_admin', 'is_admin'),
    ('no_access', 'no_access')
)

REPORT_PERMISSIONS = (
    ('is_admin', 'is_admin'),
    ('no_access', 'no_access')
)


class Position(models.Model):
    name = models.CharField(max_length=200)
    warehouse_permission = models.CharField(
        max_length=200, choices=USER_PERMISSIONS)
    users_permission = models.CharField(
        max_length=200, choices=USER_PERMISSIONS)
    tasks_permission = models.CharField(
        max_length=200, choices=TASK_PERMISSIONS)
    report_permission = models.CharField(
        max_length=200, choices=REPORT_PERMISSIONS)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Group(models.Model):
    group = models.CharField(max_length=200)
    region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.group


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=False)
    phone = models.CharField(max_length=15, validators=[validate_phone_number])
    position = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    profil_picture = models.ImageField(null=True, blank=True)

    group = models.ForeignKey(
        Group,
        verbose_name=('groups'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='accounts_users',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        related_name='accounts_users',
        related_query_name='user',
    )

    USERNAME_FIELD = "email"
    # REQUIRED_FIELDS  = ['username']

    objects = UserManager()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    def has_started_task(self):
        return self.user_tasks.filter(status='started').exists()


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=4)

    def __str__(self):
        return f"{self.user.first_name} - otp code"


class Meeting(models.Model):
    title = models.CharField(max_length=300)
    meeting_type = models.CharField(max_length=100, choices=MEETING_TYPES)
    participants = models.ManyToManyField(User, related_name='meetings')
    date = models.DateTimeField()
    meeting_description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.title}-{self.meeting_type}"


notify_type = (
    ("waiting", 'waiting'),
    ("inprogress", "inprogress"),
    ("started", "started"),
    ("completed", "completed"),
    ("created", "created")
)


class Notification(models.Model):
    task = models.ForeignKey('services.Task', on_delete=models.SET_NULL,
                             related_name='task_notifications', null=True, blank=True)
    message = models.TextField()
    users = models.ManyToManyField(User, related_name='notifications')
    read = models.ManyToManyField(User, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_email = models.EmailField(null=True, blank=True)
    user_first_name = models.CharField(max_length=255, null=True, blank=True)
    user_last_name = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(
        max_length=100, null=True, blank=True, choices=notify_type)
    report = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Notification - {self.message[:20]}"

    def is_read_by(self, user):
        return self.read.filter(id=user.id).exists()

    class Meta:
        ordering = ['-created_at']


class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name='member_rooms')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL,
                              null=True, blank=True, related_name='admin_rooms')

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_messages')
    room = models.ForeignKey(
        Room, related_name='room_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:20]}"
