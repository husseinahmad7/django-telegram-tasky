# 🔐 Django Authentication & Permissions System

## Overview

This project now uses **Django's built-in Groups and Permissions system** instead of custom Role models. This makes the auth system:

- ✅ **General-purpose** - Reusable across any Django project
- ✅ **Standard** - Uses Django's proven auth framework
- ✅ **Flexible** - Easy to extend and customize
- ✅ **Well-documented** - Extensive Django documentation available
- ✅ **Admin-friendly** - Full support in Django admin

---

## Architecture

### Models

#### 1. **TelegramUser** (extends `AbstractUser`)
- Custom user model with Telegram integration
- Inherits all Django user features (username, email, password, etc.)
- Adds Telegram-specific fields (telegram_id, telegram_username, etc.)
- Adds general fields (department, position, timezone, etc.)
- Adds notification preferences

#### 2. **UserProfile** (optional)
- One-to-one with TelegramUser
- For additional project-specific fields
- Use only if you need extra data beyond TelegramUser

#### 3. **Django's Group** (built-in)
- Represents roles (Owner, Admin, Project Manager, Developer, Viewer)
- Can have multiple permissions
- Users can belong to multiple groups

#### 4. **Django's Permission** (built-in)
- Granular permissions (e.g., "can manage projects", "can assign tasks")
- Can be assigned to groups or individual users
- Automatically created for all models (add, change, delete, view)
- Custom permissions defined in TelegramUser.Meta.permissions

---

## Custom Permissions

Defined in `core_auth/models.py`:

```python
class TelegramUser(AbstractUser):
    class Meta:
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
```

---

## Default Groups

Run `python manage.py setup_groups` to create these groups:

### 1. **Owner**
- All permissions
- Full control over everything

### 2. **Admin**
- All permissions except user management
- Can manage projects, tasks, meetings, approvals

### 3. **Project Manager**
- Manage projects and tasks
- Assign tasks
- Schedule meetings
- Request and approve approvals
- View reports

### 4. **Developer**
- View and manage tasks
- Schedule meetings
- Request approvals
- View reports

### 5. **Viewer**
- View-only access
- Can see projects, tasks, and reports
- Cannot create or edit anything

---

## Usage Examples

### 1. Assign User to Group

```python
from django.contrib.auth.models import Group
from core_auth.models import TelegramUser

# Get user and group
user = TelegramUser.objects.get(username='john')
group = Group.objects.get(name='Developer')

# Add user to group
user.groups.add(group)

# Remove user from group
user.groups.remove(group)

# Set user's groups (replaces all existing)
user.groups.set([group1, group2])

# Clear all groups
user.groups.clear()
```

### 2. Check Permissions

```python
# Check single permission
if user.has_perm('core_auth.manage_projects'):
    # User can manage projects
    pass

# Check multiple permissions (all required)
if user.has_perms(['core_auth.manage_tasks', 'core_auth.assign_tasks']):
    # User can manage and assign tasks
    pass

# Check if user has ANY of the permissions
perms = ['core_auth.manage_projects', 'core_auth.view_all_projects']
if any(user.has_perm(p) for p in perms):
    # User has at least one permission
    pass

# Using the helper method
if user.has_project_permission('manage_projects'):
    # Same as user.has_perm('core_auth.manage_projects')
    pass
```

### 3. Get User's Permissions

```python
# Get all permissions (from groups + user)
all_perms = user.get_all_permissions()
# Returns: {'core_auth.manage_tasks', 'core_auth.view_reports', ...}

# Get only group permissions
group_perms = user.get_group_permissions()

# Get user's role (first group name)
role = user.get_role_display()
# Returns: 'Developer' or 'User' if no groups
```

### 4. Assign Permissions Directly to User

```python
from django.contrib.auth.models import Permission

# Get permission
perm = Permission.objects.get(codename='manage_projects', content_type__app_label='core_auth')

# Add permission to user
user.user_permissions.add(perm)

# Remove permission
user.user_permissions.remove(perm)
```

### 5. In Views/Handlers

```python
async def create_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create a new project - requires permission."""
    user = await get_or_create_user(update, context)
    
    # Check permission
    from asgiref.sync import sync_to_async
    has_perm = await sync_to_async(user.has_project_permission)('manage_projects')
    
    if not has_perm:
        await update.message.reply_text("❌ You don't have permission to create projects.")
        return
    
    # Continue with project creation...
```

### 6. Using Decorators (for Django views)

```python
from django.contrib.auth.decorators import permission_required

@permission_required('core_auth.manage_projects')
def create_project_view(request):
    # Only users with manage_projects permission can access
    pass

@permission_required(['core_auth.manage_tasks', 'core_auth.assign_tasks'])
def assign_task_view(request):
    # User needs both permissions
    pass
```

---

## Setup Instructions

### 1. Create Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Set Up Default Groups

```bash
python manage.py setup_groups
```

This creates 5 default groups with appropriate permissions.

### 3. Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### 4. Assign Users to Groups

**Option A: Django Admin**
1. Go to http://localhost:8000/admin/
2. Click "Users"
3. Select a user
4. Scroll to "Groups" section
5. Select groups and save

**Option B: Django Shell**
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import Group
from core_auth.models import TelegramUser

user = TelegramUser.objects.get(username='john')
developer_group = Group.objects.get(name='Developer')
user.groups.add(developer_group)
```

**Option C: Programmatically in Bot**
```python
from asgiref.sync import sync_to_async
from django.contrib.auth.models import Group

async def assign_role(user, role_name):
    """Assign a role to a user."""
    group = await sync_to_async(Group.objects.get)(name=role_name)
    await sync_to_async(user.groups.add)(group)
```

---

## Migration from Old System

If you had the old `Role`, `UserProjectRole`, `TeamGroup` models:

### 1. Create New Migrations

```bash
# This will create migrations to remove old models
python manage.py makemigrations core_auth
```

### 2. Migrate Data (if needed)

Before running migrations, create a data migration to transfer old roles to groups:

```bash
python manage.py makemigrations --empty core_auth
```

Edit the migration file to transfer data:

```python
def migrate_roles_to_groups(apps, schema_editor):
    TelegramUser = apps.get_model('core_auth', 'TelegramUser')
    Group = apps.get_model('auth', 'Group')
    UserProjectRole = apps.get_model('core_auth', 'UserProjectRole')
    
    # Map old roles to new groups
    role_mapping = {
        'OWNER': 'Owner',
        'ADMIN': 'Admin',
        'MANAGER': 'Project Manager',
        'DEVELOPER': 'Developer',
        'VIEWER': 'Viewer',
    }
    
    for user_role in UserProjectRole.objects.all():
        old_role_type = user_role.role.role_type
        new_group_name = role_mapping.get(old_role_type, 'Developer')
        
        group, _ = Group.objects.get_or_create(name=new_group_name)
        user_role.user.groups.add(group)
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Set Up Groups

```bash
python manage.py setup_groups
```

---

## Advantages Over Custom Role System

### ✅ **Standard Django**
- Uses Django's proven auth framework
- Extensive documentation available
- Community support

### ✅ **Flexible**
- Users can have multiple roles (groups)
- Fine-grained permissions
- Easy to add custom permissions

### ✅ **Admin Integration**
- Full support in Django admin
- Easy to manage users and permissions
- Visual permission management

### ✅ **Reusable**
- Not tied to specific project
- Can be used in any Django project
- Easy to extend

### ✅ **Performance**
- Optimized by Django core team
- Efficient permission checking
- Caching built-in

### ✅ **Security**
- Battle-tested by millions of Django apps
- Regular security updates
- Best practices built-in

---

## Best Practices

### 1. Use Groups for Roles
```python
# ✅ Good - Use groups
user.groups.add(developer_group)

# ❌ Avoid - Assigning individual permissions
user.user_permissions.add(perm1, perm2, perm3, ...)
```

### 2. Check Permissions, Not Groups
```python
# ✅ Good - Check permission
if user.has_perm('core_auth.manage_projects'):
    ...

# ❌ Avoid - Check group membership
if user.groups.filter(name='Admin').exists():
    ...
```

### 3. Use Descriptive Permission Names
```python
# ✅ Good
('manage_projects', 'Can create, edit, and delete projects')

# ❌ Avoid
('proj_perm', 'Project permission')
```

### 4. Group Permissions Logically
```python
# ✅ Good - Related permissions together
permissions = [
    ('view_all_projects', 'Can view all projects'),
    ('manage_projects', 'Can create, edit, and delete projects'),
]

# ❌ Avoid - Random order
permissions = [
    ('manage_projects', ...),
    ('view_reports', ...),
    ('view_all_projects', ...),
]
```

---

## Troubleshooting

### Permission Not Found
```python
# Make sure migrations are run
python manage.py migrate

# Check if permission exists
from django.contrib.auth.models import Permission
Permission.objects.filter(codename='manage_projects')
```

### User Has No Permissions
```python
# Check user's groups
user.groups.all()

# Check group's permissions
group = Group.objects.get(name='Developer')
group.permissions.all()

# Re-run setup
python manage.py setup_groups
```

### Permission Check Returns False
```python
# Check exact permission string
user.has_perm('core_auth.manage_projects')  # ✅ Correct
user.has_perm('manage_projects')  # ❌ Wrong - missing app label
```

---

## Summary

**Old System:**
- Custom `Role` model with boolean fields
- `UserProjectRole` for user-project-role association
- `TeamGroup` for team management
- Project-specific and inflexible

**New System:**
- Django's `Group` model (represents roles)
- Django's `Permission` model (granular permissions)
- `TelegramUser.groups` (many-to-many)
- General-purpose and flexible

**Migration:**
1. Run `python manage.py makemigrations`
2. Run `python manage.py migrate`
3. Run `python manage.py setup_groups`
4. Assign users to groups in admin or programmatically

**Usage:**
- `user.groups.add(group)` - Assign role
- `user.has_perm('core_auth.manage_projects')` - Check permission
- `user.get_role_display()` - Get role name

---

**🎉 Your auth system is now general-purpose and follows Django best practices!**

