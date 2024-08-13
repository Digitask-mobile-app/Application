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


USER_TYPE = (
    ("Texnik", "Texnik"),
    ("Plumber", "Plumber"),
    ("Ofis menecer", "Ofis menecer"),
    ("Texnik menecer", "Texnik menecer"),
)

AUTH_PROVIDERS = {'email': 'email'}


class Group(models.Model):
    group = models.CharField(max_length=200)
    region = models.CharField(max_length=200)

    def __str__(self):
        return self.group


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=False)
    phone = models.CharField(max_length=15, validators=[validate_phone_number])
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
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

    @property
    def is_texnik(self):
        return self.user_type == "Texnik"

    @property
    def is_plumber(self):
        return self.user_type == "Plumber"

    @property
    def is_ofis_menecer(self):
        return self.user_type == "Ofis menecer"

    @property
    def is_texnik_menecer(self):
        return self.user_type == "Texnik menecer"


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


class Notification(models.Model):
    message = models.TextField()
    users = models.ManyToManyField(User, related_name='notifications')
    read = models.ManyToManyField(User, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_email = models.EmailField()

    def __str__(self):
        return f"Notification - {self.message[:20]}"

    def is_read_by(self, user):
        return self.read.filter(id=user.id).exists()

    class Meta:
        ordering = ['-created_at']
