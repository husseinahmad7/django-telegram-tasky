# Modular Bot Architecture

## Overview

The Tasky bot now uses a **modular, scalable architecture** that allows you to easily add or remove features by simply adding or removing Django apps from `INSTALLED_APPS`.

## How It Works

### 1. **Dynamic Handler Registration**

Each Django app can define a `bot_config.py` file that specifies:
- **Handlers**: Command handlers, conversation handlers, callback handlers
- **Menu Buttons**: Buttons to show in the main menu
- **Help Text**: Documentation for the app's commands

### 2. **Handler Registry**

The `core_bot.registry` module automatically:
- Discovers all apps with `bot_config.py`
- Registers their handlers with the bot
- Builds the menu dynamically
- Generates help text from all apps

### 3. **App Independence**

Each app is self-contained:
- Has its own handlers in `app_name/handlers/`
- Defines its own bot configuration in `app_name/bot_config.py`
- Can be enabled/disabled by adding/removing from `INSTALLED_APPS`

## Creating a New Bot App

### Step 1: Create the App Structure

```bash
python manage.py startapp my_feature
mkdir my_feature/handlers
touch my_feature/handlers/__init__.py
```

### Step 2: Create Handlers

Create `my_feature/handlers/my_handlers.py`:

```python
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes
from core_bot.utils import get_or_create_user, KeyboardBuilder, MessageFormatter

async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle my custom command."""
    user = await get_or_create_user(update, context)
    
    msg = f"{MessageFormatter.EMOJI['success']} Hello {user.telegram_name}!"
    
    keyboard = KeyboardBuilder.build_menu(
        [KeyboardBuilder.back_button("menu")],
        n_cols=1
    )
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
```

Export handlers in `my_feature/handlers/__init__.py`:

```python
from .my_handlers import my_command

__all__ = ['my_command']
```

### Step 3: Create Bot Configuration

Create `my_feature/bot_config.py`:

```python
"""
Bot configuration for my_feature app.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler
from core_bot.utils import MessageFormatter

# App metadata
APP_NAME = "My Feature"
APP_EMOJI = "🎯"
APP_DESCRIPTION = "My awesome feature"
APP_ORDER = 10  # Order in menu (lower = higher priority)

# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="my_feature"
        )
    ]

# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers import my_command
    
    # Command handlers
    application.add_handler(CommandHandler("mycommand", my_command))
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(my_command, pattern="^my_feature$"))

# Help text
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} My Feature:</b>
/mycommand - Do something awesome
"""
```

### Step 4: Add to INSTALLED_APPS

Edit `Tasky/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Core apps
    'core_auth',
    'core_bot',
    'core_tasks',
    'my_feature',  # ← Add your app here
]
```

### Step 5: Restart the Bot

```bash
python start_bot.py
```

Your feature is now automatically:
- ✅ Registered with the bot
- ✅ Shown in the main menu
- ✅ Included in help text
- ✅ Ready to use!

## Removing an App

To remove a feature, simply:

1. **Remove from INSTALLED_APPS** in `Tasky/settings.py`
2. **Restart the bot**

That's it! The menu and help text will automatically update.

## Example: Removing Tasks Feature

To remove the tasks feature:

```python
# Tasky/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Core apps
    'core_auth',
    'core_bot',
    # 'core_tasks',  # ← Comment out or remove
]
```

Restart the bot, and the Tasks button will disappear from the menu!

## App Configuration Reference

### Required Functions

#### `register_handlers(application)`
Registers all handlers for the app.

**Parameters:**
- `application`: The Telegram bot application instance

**Example:**
```python
def register_handlers(application):
    from .handlers import my_handler
    application.add_handler(CommandHandler("mycommand", my_handler))
```

### Optional Functions

#### `get_menu_buttons()`
Returns a list of `InlineKeyboardButton` objects to show in the main menu.

**Returns:** `List[InlineKeyboardButton]`

**Example:**
```python
def get_menu_buttons():
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton("🎯 My Feature", callback_data="my_feature")
    ]
```

#### `get_help_text()`
Returns help text for the app's commands.

**Returns:** `str` (HTML formatted)

**Example:**
```python
def get_help_text():
    return """
<b>🎯 My Feature:</b>
/mycommand - Do something
/another - Do something else
"""
```

### Optional Metadata

- `APP_NAME`: Display name (default: app name)
- `APP_EMOJI`: Emoji for menu button (default: 📦)
- `APP_DESCRIPTION`: Short description
- `APP_ORDER`: Menu order, lower = higher priority (default: 999)

## Current Apps

### core_bot (Order: 0) - Required
Core bot functionality - always loaded first
- Basic commands: /start, /help, /menu
- Reports: /dailyreport, /weeklyreport

### core_tasks (Order: 2) - Required
Task management + ALL database models
- Task commands: /tasks, /mytasks, /createtask
- Task tracking and assignment
- **Contains all models:** Project, Task, Meeting, Approval, Alert, etc.

### core_projects (Order: 1) - Optional
Project management handlers
- Project commands: /projects, /myprojects, /createproject
- Project tracking and team management

### core_meetings (Order: 3) - Optional
Meeting management handlers
- Meeting commands: /meetings, /schedulemeeting
- Meeting voting and scheduling

### core_approvals (Order: 4) - Optional
Approval workflow handlers
- Approval commands: /approvals, /approve, /reject
- Approval requests and responses

### core_notifications (Order: 5) - Optional
Notification handlers
- Notification commands: /notifications, /settings
- Alert management

## Benefits

### ✅ **Scalability**
- Add new features without modifying core code
- Each app is independent and self-contained

### ✅ **Maintainability**
- Clear separation of concerns
- Easy to find and fix bugs in specific features

### ✅ **Flexibility**
- Enable/disable features per deployment
- Different bots can use different feature sets

### ✅ **Team Development**
- Multiple developers can work on different apps
- No merge conflicts in handler registration

## Best Practices

1. **Keep apps focused**: One app = one feature domain
2. **Use meaningful names**: `core_tasks` not `app1`
3. **Set appropriate order**: Core features first (low order), optional features last (high order)
4. **Document commands**: Always provide help text
5. **Handle errors**: Use try/except in handlers
6. **Test independently**: Each app should work standalone

## Troubleshooting

### App not showing in menu

**Check:**
1. Is the app in `INSTALLED_APPS`?
2. Does it have `bot_config.py`?
3. Does `bot_config.py` have `get_menu_buttons()`?
4. Did you restart the bot?

### Handlers not working

**Check:**
1. Is `register_handlers()` defined?
2. Are handlers imported correctly?
3. Check the logs for errors during registration
4. Verify handler patterns don't conflict

### Import errors

**Check:**
1. Are all dependencies installed?
2. Is the app structure correct?
3. Are `__init__.py` files present?
4. Check Python path and imports

## Advanced: Conversation Handlers

For complex multi-step interactions:

```python
from telegram.ext import ConversationHandler, MessageHandler, filters

# Define states
STATE_1, STATE_2 = range(2)

def register_handlers(application):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start_flow", start_flow)],
        states={
            STATE_1: [MessageHandler(filters.TEXT, handle_state_1)],
            STATE_2: [MessageHandler(filters.TEXT, handle_state_2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=False,
    )
    application.add_handler(conv_handler)
```

## Summary

The modular architecture makes Tasky:
- **Easy to extend**: Add features by creating new apps
- **Easy to customize**: Remove unwanted features
- **Easy to maintain**: Clear code organization
- **Easy to scale**: Independent app development

Just create a `bot_config.py`, add to `INSTALLED_APPS`, and you're done! 🚀

