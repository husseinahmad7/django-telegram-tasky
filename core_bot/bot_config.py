"""
Bot configuration for core_bot app.
Defines basic handlers and core functionality (start, help, menu, reports).
"""
from telegram.ext import CommandHandler, CallbackQueryHandler
from core_bot.utils import MessageFormatter


# App metadata
APP_NAME = "Core"
APP_EMOJI = "🏠"
APP_DESCRIPTION = "Core bot functionality"
APP_ORDER = 0  # Always first


# This app doesn't add menu buttons (it provides the menu itself)
def get_menu_buttons():
    """Return menu buttons for this app."""
    return []


# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from core_bot.handlers.basic import start, help_command, menu
    from core_bot.handlers.reports import daily_report, weekly_report

    # Basic commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))

    # Report commands
    application.add_handler(CommandHandler("dailyreport", daily_report))
    application.add_handler(CommandHandler("weeklyreport", weekly_report))

    # Callback query handlers
    application.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))


# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>📊 Reports:</b>
/dailyreport - Submit daily report
/weeklyreport - View weekly summary
/progress [project_id] - Project progress

<b>⚙️ Settings:</b>
/settings - User preferences
/timezone [tz] - Set timezone
/language [lang] - Set language
"""

