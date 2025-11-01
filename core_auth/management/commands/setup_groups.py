"""
Management command to set up default groups and permissions.
Run with: python manage.py setup_groups
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core_auth.models import TelegramUser


class Command(BaseCommand):
    help = 'Set up default groups and permissions for the application'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up groups and permissions...'))
        
        # Get content type for TelegramUser (where custom permissions are defined)
        user_content_type = ContentType.objects.get_for_model(TelegramUser)
        
        # Define groups and their permissions
        groups_permissions = {
            'Owner': [
                # All permissions
                'view_all_projects', 'manage_projects',
                'view_all_tasks', 'manage_tasks', 'assign_tasks',
                'schedule_meetings', 'manage_meetings',
                'request_approvals', 'approve_requests',
                'view_reports', 'export_data',
                'manage_users',
            ],
            'Admin': [
                'view_all_projects', 'manage_projects',
                'view_all_tasks', 'manage_tasks', 'assign_tasks',
                'schedule_meetings', 'manage_meetings',
                'request_approvals', 'approve_requests',
                'view_reports', 'export_data',
            ],
            'Project Manager': [
                'view_all_projects', 'manage_projects',
                'view_all_tasks', 'manage_tasks', 'assign_tasks',
                'schedule_meetings', 'manage_meetings',
                'request_approvals', 'approve_requests',
                'view_reports',
            ],
            'Developer': [
                'view_all_tasks', 'manage_tasks',
                'schedule_meetings',
                'request_approvals',
                'view_reports',
            ],
            'Viewer': [
                'view_all_projects',
                'view_all_tasks',
                'view_reports',
            ],
        }
        
        created_count = 0
        updated_count = 0
        
        for group_name, permission_codenames in groups_permissions.items():
            # Create or get group
            group, created = Group.objects.get_or_create(name=group_name)
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created group: {group_name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  → Updating group: {group_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Add permissions
            for codename in permission_codenames:
                try:
                    permission = Permission.objects.get(
                        codename=codename,
                        content_type=user_content_type
                    )
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'    ⚠ Permission not found: {codename}')
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'    Added {len(permission_codenames)} permissions')
            )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS(f'✓ Setup complete!'))
        self.stdout.write(self.style.SUCCESS(f'  Created: {created_count} groups'))
        self.stdout.write(self.style.SUCCESS(f'  Updated: {updated_count} groups'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('Usage:')
        self.stdout.write('  1. Assign users to groups in Django admin')
        self.stdout.write('  2. Or use: user.groups.add(group)')
        self.stdout.write('  3. Check permissions: user.has_perm("core_auth.manage_projects")')
        self.stdout.write('')
        self.stdout.write('Available groups:')
        for group_name in groups_permissions.keys():
            self.stdout.write(f'  - {group_name}')

