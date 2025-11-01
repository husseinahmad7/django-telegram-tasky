"""
Admin configuration for core_auth app.
Uses Django's built-in Groups and Permissions system.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import TelegramUser, UserProfile


@admin.register(TelegramUser)
class TelegramUserAdmin(BaseUserAdmin):
    """
    Admin for TelegramUser with Groups and Permissions support.
    """
    list_display = [
        'username', 'telegram_username', 'email',
        'department', 'position', 'get_groups', 'is_active', 'is_staff'
    ]
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'groups', 'department']
    search_fields = ['username', 'telegram_username', 'email', 'first_name', 'last_name', 'telegram_id']

    filter_horizontal = ['groups', 'user_permissions']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Telegram Info', {
            'fields': (
                'telegram_id', 'telegram_username',
                'telegram_first_name', 'telegram_last_name'
            )
        }),
        ('Profile Info', {
            'fields': ('department', 'position', 'phone_number')
        }),
        ('Preferences', {
            'fields': ('language_code', 'timezone', 'is_bot_active')
        }),
        ('Notification Settings', {
            'fields': (
                'notify_task_assigned', 'notify_deadline_approaching',
                'notify_meeting_scheduled', 'notify_approval_required'
            ),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('telegram_id', 'telegram_username', 'email')
        }),
    )

    def get_groups(self, obj):
        """Display user's groups."""
        return ", ".join([g.name for g in obj.groups.all()]) or "No groups"
    get_groups.short_description = 'Groups'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for optional UserProfile."""
    list_display = ['user', 'github_username', 'created_at']
    search_fields = ['user__username', 'github_username']
    raw_id_fields = ['user']


# Customize Group admin to show permissions better
class GroupAdmin(admin.ModelAdmin):
    """Enhanced Group admin."""
    list_display = ['name', 'get_permissions_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']

    def get_permissions_count(self, obj):
        """Display number of permissions."""
        return obj.permissions.count()
    get_permissions_count.short_description = 'Permissions'


# Unregister the default Group admin and register our custom one
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
