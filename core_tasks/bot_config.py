"""
Bot configuration for core_tasks app.
Defines handlers for task management only.
Note: This app also contains all models (Project, Task, Meeting, Approval, Alert, etc.)
but only provides handlers for tasks. Other features have their own handler apps.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from core_bot.utils import MessageFormatter


# App metadata
APP_NAME = "Tasks"
APP_EMOJI = "📝"
APP_DESCRIPTION = "Task management and tracking"
APP_ORDER = 2  # Order in menu (lower = higher priority)


# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="list_tasks"
        )
    ]


# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers import (
        list_tasks, task_detail, update_task_status, create_task,
        task_title_received, task_desc_received, task_priority_received,
        task_deadline_received, assign_task,
        TASK_TITLE, TASK_DESC, TASK_PRIORITY, TASK_DEADLINE
    )
    
    # Task commands
    application.add_handler(CommandHandler("tasks", list_tasks))
    application.add_handler(CommandHandler("mytasks", list_tasks))
    
    # Task creation conversation
    task_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("createtask", create_task),
            CallbackQueryHandler(create_task, pattern="^create_task:")
        ],
        states={
            TASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_title_received)],
            TASK_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_desc_received)],
            TASK_PRIORITY: [CallbackQueryHandler(task_priority_received, pattern="^task_priority:")],
            TASK_DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_deadline_received)],
        },
        fallbacks=[],
        per_message=False,
    )
    application.add_handler(task_conv_handler)
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(list_tasks, pattern="^(list_tasks|my_tasks)"))
    application.add_handler(CallbackQueryHandler(task_detail, pattern=r"^task:\d+$"))
    application.add_handler(CallbackQueryHandler(update_task_status, pattern="^task_status:"))
    application.add_handler(CallbackQueryHandler(assign_task, pattern="^assign_task:"))
    
    # Pagination handlers
    application.add_handler(CallbackQueryHandler(list_tasks, pattern=r"^list_tasks_(all|my):\d+$"))


# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} Task Management:</b>
/tasks - List all tasks
/mytasks - Your assigned tasks
/createtask - Create new task
/task [id] - View task details
/assign [task_id] [user] - Assign task
/status [task_id] [status] - Update task status
"""

