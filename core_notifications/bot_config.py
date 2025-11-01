"""
Bot configuration for core_notifications app.
Defines handlers for notifications and alerts.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler
from core_bot.utils import MessageFormatter

# App metadata
APP_NAME = "Notifications"
APP_EMOJI = "🔔"
APP_DESCRIPTION = "Notifications and alerts"
APP_ORDER = 5  # Order in menu

# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="notifications"
        )
    ]

# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers.notifications import (
        list_notifications, notification_detail, mark_all_read,
        list_reminders, notification_settings, toggle_notification
    )
    
    # Notification commands
    application.add_handler(CommandHandler("notifications", list_notifications))
    application.add_handler(CommandHandler("reminders", list_reminders))
    application.add_handler(CommandHandler("settings", notification_settings))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(list_notifications, pattern="^notifications"))
    application.add_handler(CallbackQueryHandler(notification_detail, pattern=r"^notification:\d+$"))
    application.add_handler(CallbackQueryHandler(mark_all_read, pattern="^mark_all_read$"))
    application.add_handler(CallbackQueryHandler(notification_settings, pattern="^settings$"))
    application.add_handler(CallbackQueryHandler(toggle_notification, pattern="^toggle_notif:"))

# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} Notifications:</b>
/notifications - View all notifications
/settings - Notification preferences
"""

