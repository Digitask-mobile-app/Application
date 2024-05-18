from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.contrib.auth.models import Group, Permission
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import validate_phone_number


USER_TYPE = (
    ("technician", "technician"),
    ("plumber", "plumber"),
    ("office_manager", "office_manager"),
    ("tech_manager", "tech_manager"),
)

AUTH_PROVIDERS ={'email':'email'}

class Group(models.Model):
    group = models.CharField(max_length=200)
    region = models.CharField(max_length=200)

    def __str__(self):
        return self.group


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=15, validators=[validate_phone_number])
    user_type = models.CharField(max_length=20, choices=USER_TYPE)
    group = models.ForeignKey(Group, on_delete = models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
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
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELD = "username"

    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }


    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    @property
    def is_technician(self):
        return self.user_type == "technician"

    @property
    def is_plumber(self):
        return self.user_type == "plumber"
    
    @property
    def is_office_manager(self):
        return self.user_type == "office_manager"

    @property
    def is_tech_manager(self):
        return self.user_type == "tech_manager"
    


    
class OneTimePassword(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    otp=models.CharField(max_length=6)


    def __str__(self):
        return f"{self.user.first_name} - otp code"
    
