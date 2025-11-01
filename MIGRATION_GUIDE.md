# 📦 Migration Guide

Guide for migrating from old structure to new modular architecture.

## Overview

The project has been restructured into reusable core apps:

- **core_auth** - User management, roles, permissions
- **core_tasks** - Project and task management
- **core_bot** - Telegram bot handlers and utilities

Old apps (`Bot`, `ProjectMng`) are deprecated but kept for reference.

## Migration Steps

### 1. Backup Current Data

```bash
# Backup database
cp db.sqlite3 db.sqlite3.backup

# Or export data
python manage.py dumpdata > backup.json
```

### 2. Install New Dependencies

```bash
# Using UV
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 3. Update Settings

The new `settings.py` includes:
- Custom user model: `AUTH_USER_MODEL = 'core_auth.TelegramUser'`
- New apps: `core_auth`, `core_bot`, `core_tasks`
- Environment variable loading with `python-dotenv`

### 4. Create New Migrations

```bash
# Remove old migrations if starting fresh
rm -rf core_auth/migrations/
rm -rf core_tasks/migrations/
rm -rf core_bot/migrations/

# Create new migrations
python manage.py makemigrations core_auth
python manage.py makemigrations core_tasks
python manage.py makemigrations core_bot
```

### 5. Migrate Database

**Option A: Fresh Start (Recommended for development)**

```bash
# Delete old database
rm db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Option B: Migrate Existing Data**

```bash
# Run migrations
python manage.py migrate

# Migrate data from old models to new
python manage.py shell
```

```python
from django.contrib.auth.models import User
from core_auth.models import TelegramUser
from ProjectMng.models import Project as OldProject
from core_tasks.models import Project as NewProject

# Migrate users
for old_user in User.objects.all():
    TelegramUser.objects.get_or_create(
        username=old_user.username,
        defaults={
            'email': old_user.email,
            'first_name': old_user.first_name,
            'last_name': old_user.last_name,
            'is_staff': old_user.is_staff,
            'is_superuser': old_user.is_superuser,
        }
    )

# Migrate projects (if you have data)
# Note: You'll need to adapt this based on your actual data
```

### 6. Update Bot Configuration

The new bot is in `core_bot/bot.py` and uses:
- Modern handler structure
- Conversation handlers for multi-step flows
- Inline keyboards with pagination
- Reusable utilities

Old bot files in `Bot/` can be removed after migration.

### 7. Update ASGI Configuration

`Tasky/asgi.py` now:
- Imports from `core_bot.bot`
- Uses environment variable for webhook URL
- Cleaner lifecycle management

### 8. Test the Migration

```bash
# Start the bot
python start_bot.py

# Or manually
python manage.py set_webhook https://your-url.ngrok-free.app
uvicorn Tasky.asgi:app --reload
```

Test in Telegram:
1. Send `/start`
2. Create a project
3. Create a task
4. Test all commands

## Key Differences

### Old Structure
```
Bot/
  telegram_bot.py  # All handlers in one file
  bot.py           # Bot setup
ProjectMng/
  models.py        # All models together
```

### New Structure
```
core_auth/
  models.py        # User, Role, TeamGroup
core_tasks/
  models.py        # Project, Task, Meeting, etc.
core_bot/
  bot.py           # Bot configuration
  utils.py         # Reusable utilities
  handlers/        # Organized handlers
    basic.py
    projects.py
    tasks.py
    ...
```

## Benefits of New Structure

1. **Modularity** - Core apps can be reused in other projects
2. **Separation of Concerns** - Clear boundaries between auth, tasks, and bot
3. **Scalability** - Easy to add new features
4. **Maintainability** - Organized code structure
5. **Testability** - Each component can be tested independently

## Reusing Core Apps

The core apps are designed to be reusable:

### In Another Django Project

```python
# settings.py
INSTALLED_APPS = [
    ...
    'core_auth',
    'core_tasks',
    # Don't include core_bot if you don't need Telegram
]

AUTH_USER_MODEL = 'core_auth.TelegramUser'
```

### In Another Bot Project

```python
# your_bot.py
from core_bot.utils import ModelManager, KeyboardBuilder, MessageFormatter
from core_bot.handlers.basic import start, help_command

# Use the utilities and handlers
```

## Cleanup Old Files

After successful migration:

```bash
# Remove old apps (optional)
rm -rf Bot/
rm -rf ProjectMng/

# Remove old files
rm bot_run.py
rm run.py
rm Pipfile
rm Pipfile.lock
```

## Rollback

If you need to rollback:

```bash
# Restore database
cp db.sqlite3.backup db.sqlite3

# Or restore from JSON
python manage.py loaddata backup.json

# Checkout old code
git checkout previous-commit
```

## Common Issues

### Import Errors

Make sure all apps are in `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    ...
    'core_auth',
    'core_bot',
    'core_tasks',
]
```

### Migration Conflicts

```bash
# Reset migrations
python manage.py migrate --fake core_auth zero
python manage.py migrate --fake core_tasks zero
python manage.py migrate --fake core_bot zero

# Re-run
python manage.py migrate
```

### User Model Issues

If you get user model errors:
1. Make sure `AUTH_USER_MODEL = 'core_auth.TelegramUser'` is set
2. Delete database and start fresh
3. Or create a custom migration

## Support

For issues during migration:
1. Check Django logs
2. Verify all dependencies are installed
3. Ensure `.env` is configured correctly
4. Test with a fresh database first

---

Good luck with your migration! 🚀

