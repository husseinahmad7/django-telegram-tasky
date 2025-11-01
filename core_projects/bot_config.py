"""
Bot configuration for core_projects app.
Defines handlers for project management.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from core_bot.utils import MessageFormatter

# App metadata
APP_NAME = "Projects"
APP_EMOJI = "📁"
APP_DESCRIPTION = "Project management and tracking"
APP_ORDER = 1  # Order in menu (lower = higher priority)

# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="list_projects"
        )
    ]

# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers.projects import (
        list_projects, project_detail, create_project,
        project_name_received, project_desc_received, project_priority_received,
        cancel_project_creation, PROJECT_NAME, PROJECT_DESC, PROJECT_PRIORITY
    )
    
    # Project commands
    application.add_handler(CommandHandler("projects", list_projects))
    application.add_handler(CommandHandler("myprojects", list_projects))
    
    # Project creation conversation
    project_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("createproject", create_project),
            CallbackQueryHandler(create_project, pattern="^create_project$")
        ],
        states={
            PROJECT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_name_received)],
            PROJECT_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, project_desc_received)],
            PROJECT_PRIORITY: [CallbackQueryHandler(project_priority_received, pattern="^priority:")],
        },
        fallbacks=[CommandHandler("cancel", cancel_project_creation)],
        per_message=False,
    )
    application.add_handler(project_conv_handler)
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(list_projects, pattern="^(list_projects|my_projects)"))
    application.add_handler(CallbackQueryHandler(project_detail, pattern=r"^project:\d+$"))
    
    # Pagination handlers
    application.add_handler(CallbackQueryHandler(list_projects, pattern=r"^list_projects:\d+$"))

# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} Project Management:</b>
/projects - List all projects
/myprojects - Your projects
/createproject - Create new project
/project [id] - View project details
"""

