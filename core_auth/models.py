"""
Core authentication models for user management.
Reusable across projects - uses Django's built-in Groups and Permissions.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class TelegramUser(AbstractUser):
    """
    Extended user model with Telegram integration.

    Uses Django's built-in Groups and Permissions system:
    - user.groups.all() - Get user's groups
    - user.user_permissions.all() - Get user's permissions
    - user.has_perm('app.permission_name') - Check permission
    - user.has_perms(['app.perm1', 'app.perm2']) - Check multiple permissions
    - user.get_all_permissions() - Get all permissions (from groups + user)
    - user.get_group_permissions() - Get permissions from groups only
    """

    # Telegram-specific fields
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, db_index=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    telegram_first_name = models.CharField(max_length=255, blank=True)
    telegram_last_name = models.CharField(max_length=255, blank=True)

    # General user fields (reusable across projects)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    language_code = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')

    # Bot-specific settings
    is_bot_active = models.BooleanField(default=True, help_text=_('Whether user can access the bot'))

    # Notification preferences (can be customized per project)
    notify_task_assigned = models.BooleanField(default=True)
    notify_deadline_approaching = models.BooleanField(default=True)
    notify_meeting_scheduled = models.BooleanField(default=True)
    notify_approval_required = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
        permissions = [
            # Project permissions
            ('view_all_projects', 'Can view all projects'),
            ('manage_projects', 'Can create, edit, and delete projects'),

            # Task permissions
            ('view_all_tasks', 'Can view all tasks'),
            ('manage_tasks', 'Can create, edit, and delete tasks'),
            ('assign_tasks', 'Can assign tasks to users'),

            # Meeting permissions
            ('schedule_meetings', 'Can schedule meetings'),
            ('manage_meetings', 'Can edit and delete meetings'),

            # Approval permissions
            ('request_approvals', 'Can request approvals'),
            ('approve_requests', 'Can approve/reject approval requests'),

            # Report permissions
            ('view_reports', 'Can view reports and analytics'),
            ('export_data', 'Can export data'),

            # User management
            ('manage_users', 'Can manage users and permissions'),
        ]

    def __str__(self):
        return self.get_full_name() or self.username or f"User {self.telegram_id}"

    @property
    def telegram_name(self):
        """Get Telegram display name."""
        if self.telegram_first_name:
            name = self.telegram_first_name
            if self.telegram_last_name:
                name += f" {self.telegram_last_name}"
            return name
        return self.telegram_username or self.username

    def has_project_permission(self, permission_codename):
        """
        Check if user has a specific permission.

        Args:
            permission_codename: e.g., 'manage_projects', 'view_all_tasks'

        Returns:
            bool: True if user has permission
        """
        return self.has_perm(f'core_auth.{permission_codename}')

    def get_role_display(self):
        """Get user's primary role (first group name)."""
        groups = self.groups.all()
        if groups:
            return groups[0].name
        return 'User'


class UserProfile(models.Model):
    """
    Extended user profile for additional project-specific data.
    Optional - use only if you need extra fields beyond TelegramUser.
    """
    user = models.OneToOneField(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Add any project-specific fields here
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)

    # Social links
    github_username = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)

    # Work preferences
    working_hours_start = models.TimeField(null=True, blank=True)
    working_hours_end = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')

    def __str__(self):
        return f"Profile: {self.user}"
