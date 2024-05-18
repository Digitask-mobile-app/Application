from django.contrib import admin
from .models import User, OneTimePassword, Group, Meeting
# Register your models here.

admin.site.register(User)
admin.site.register(OneTimePassword)
admin.site.register(Group)
admin.site.register(Meeting)