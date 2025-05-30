from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext, gettext_lazy as _
from .models import User, OneTimePassword, Group, Meeting, Notification, Room, Message, Position, Region
from django.urls import reverse
from django.utils.html import format_html


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'position',
         'group', 'timestamp', 'is_online', 'latitude', 'longitude', 'profil_picture')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff',
         'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'phone', 'latitude', 'longitude',
                    'position', 'timestamp', 'is_online', 'group', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)

    def change_password_link(self, obj):
        return format_html('<a href="{}">Change Password</a>', reverse('password-reset'))

    change_password_link.short_description = 'Password Reset'

    # def get_fieldsets(self, request, obj=None):
    #     if obj and obj.is_staff and obj.is_superuser:
    #         return (
    #             (None, {'fields': ('email', 'password')}),
    #             ('Personal info', {'fields': ('first_name', 'last_name', 'phone')}),
    #             ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    #             (_('Important dates'), {'fields': ('last_login',)}),
    #         )
    #     return super().get_fieldsets(request, obj)


admin.site.register(User, UserAdmin)
admin.site.register(OneTimePassword)
admin.site.register(Region)
admin.site.register(Group)
admin.site.register(Meeting)
admin.site.register(Notification)
admin.site.register(Message)
admin.site.register(Room)
admin.site.register(Position)
