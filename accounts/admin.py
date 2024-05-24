from django.contrib import admin
from .models import User, OneTimePassword, Group, Meeting
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from django.urls import reverse
from django.utils.html import format_html

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'user_type', 'group')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'change_password_link')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    def change_password_link(self, obj):
        return format_html('<a href="{}">Change Password</a>', reverse('password-reset'))

    change_password_link.short_description = 'Password Reset'

admin.site.register(User, UserAdmin)
admin.site.register(OneTimePassword)
admin.site.register(Group)
admin.site.register(Meeting)