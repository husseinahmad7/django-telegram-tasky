"""
Main bot application configuration.
Reusable bot setup with all handlers.
"""
import logging
import sys
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters, ContextTypes
)
from django.conf import settings

# Setup logging
logger = logging.getLogger(__name__)

# Import handlers
from core_bot.handlers.basic import start, help_command, menu
from core_bot.handlers.projects import (
    list_projects, project_detail, create_project,
    project_name_received, project_desc_received, project_priority_received,
    cancel_project_creation, PROJECT_NAME, PROJECT_DESC, PROJECT_PRIORITY
)
from core_bot.handlers.tasks import (
    list_tasks, task_detail, update_task_status, create_task,
    task_title_received, task_desc_received, task_priority_received,
    task_deadline_received, assign_task,
    TASK_TITLE, TASK_DESC, TASK_PRIORITY, TASK_DEADLINE
)
from core_bot.handlers.reports import daily_report, weekly_report
from core_bot.handlers.meetings import (
    list_meetings, schedule_meeting, meeting_detail,
    meeting_title_received, meeting_desc_received,
    meeting_project_received, meeting_time_received,
    meeting_vote, submit_vote, view_meeting_votes,
    cancel_meeting_creation,
    MEETING_TITLE, MEETING_DESC, MEETING_PROJECT, MEETING_TIME
)
from core_bot.handlers.approvals import (
    list_approvals, approval_detail, request_approval,
    approval_type_received, approval_item_received,
    approval_reason_received, approve_action, reject_action,
    cancel_approval_request, approve_task, reject_task,
    APPROVAL_TYPE, APPROVAL_ITEM, APPROVAL_REASON
)
from core_bot.handlers.notifications import (
    list_notifications, notification_detail, mark_all_read,
    list_reminders, notification_settings, toggle_notification
)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

    # Try to notify the user
    try:
        error_message = (
            "❌ <b>Oops! Something went wrong.</b>\n\n"
            "Please try again or use /menu to return to the main menu.\n\n"
            "If the problem persists, contact support."
        )

        if update and update.effective_message:
            await update.effective_message.reply_text(error_message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


def create_bot_application():
    """Create and configure the bot application."""

    # Fix for PyInstaller: Configure httpx to work with frozen executables
    if getattr(sys, 'frozen', False):
        # Running as executable - use custom HTTP configuration
        from telegram.request import HTTPXRequest
        from httpx import Limits

        # Create request object with custom settings for PyInstaller
        request = HTTPXRequest(
            connection_pool_size=1,  # Minimal pool size
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
            http_version="1.1",  # Use HTTP/1.1 instead of HTTP/2
        )

        # Build application with custom request
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).request(request).build()
    else:
        # Running as script - use default configuration
        bot = Bot(settings.TELEGRAM_BOT_TOKEN)
        application = ApplicationBuilder().bot(bot).build()
    
    # Basic commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu))
    
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
        fallbacks=[CommandHandler("cancel", cancel_project_creation)],
        per_message=False,
    )
    application.add_handler(task_conv_handler)
    
    # Report commands
    application.add_handler(CommandHandler("dailyreport", daily_report))
    application.add_handler(CommandHandler("weeklyreport", weekly_report))

    # Meeting conversation handler
    meeting_conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("schedulemeeting", schedule_meeting),
            CallbackQueryHandler(schedule_meeting, pattern="^schedule_meeting$")
        ],
        states={
            MEETING_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, meeting_title_received)],
            MEETING_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, meeting_desc_received)],
            MEETING_PROJECT: [CallbackQueryHandler(meeting_project_received, pattern="^meeting_project:")],
            MEETING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, meeting_time_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel_meeting_creation)],
        per_message=False,
    )
    application.add_handler(meeting_conv_handler)

    # Meeting commands
    application.add_handler(CommandHandler("meetings", list_meetings))
    
    # Approval conversation handler
    approval_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("requestapproval", request_approval)],
        states={
            APPROVAL_TYPE: [CallbackQueryHandler(approval_type_received, pattern="^approval_type:")],
            APPROVAL_ITEM: [CallbackQueryHandler(approval_item_received, pattern="^approval_item:")],
            APPROVAL_REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, approval_reason_received)],
        },
        fallbacks=[CallbackQueryHandler(cancel_approval_request, pattern="^cancel_approval$")],
        per_message=False,
    )
    application.add_handler(approval_conv_handler)

    # Approval commands
    application.add_handler(CommandHandler("approvals", list_approvals))
    application.add_handler(CommandHandler("approve", approve_task))
    application.add_handler(CommandHandler("reject", reject_task))

    # Notification commands
    application.add_handler(CommandHandler("notifications", list_notifications))
    application.add_handler(CommandHandler("reminders", list_reminders))
    application.add_handler(CommandHandler("settings", notification_settings))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(list_projects, pattern="^(list_projects|my_projects)"))
    application.add_handler(CallbackQueryHandler(project_detail, pattern="^project:\d+$"))
    application.add_handler(CallbackQueryHandler(list_tasks, pattern="^(list_tasks|my_tasks)"))
    application.add_handler(CallbackQueryHandler(task_detail, pattern="^task:\d+$"))
    application.add_handler(CallbackQueryHandler(update_task_status, pattern="^task_status:"))
    application.add_handler(CallbackQueryHandler(assign_task, pattern="^assign_task:"))
    application.add_handler(CallbackQueryHandler(list_meetings, pattern="^list_meetings"))
    application.add_handler(CallbackQueryHandler(meeting_detail, pattern="^meeting:\d+$"))
    application.add_handler(CallbackQueryHandler(meeting_vote, pattern="^vote_meeting:"))
    application.add_handler(CallbackQueryHandler(submit_vote, pattern="^vote_submit:"))
    application.add_handler(CallbackQueryHandler(view_meeting_votes, pattern="^meeting_votes:"))
    application.add_handler(CallbackQueryHandler(list_approvals, pattern="^list_approvals"))
    application.add_handler(CallbackQueryHandler(approval_detail, pattern="^approval:\d+$"))
    application.add_handler(CallbackQueryHandler(approve_action, pattern="^approve_action:"))
    application.add_handler(CallbackQueryHandler(reject_action, pattern="^reject_action:"))
    application.add_handler(CallbackQueryHandler(list_notifications, pattern="^notifications"))
    application.add_handler(CallbackQueryHandler(notification_detail, pattern="^notification:\d+$"))
    application.add_handler(CallbackQueryHandler(mark_all_read, pattern="^mark_all_read$"))
    application.add_handler(CallbackQueryHandler(notification_settings, pattern="^settings$"))
    application.add_handler(CallbackQueryHandler(toggle_notification, pattern="^toggle_notif:"))

    # Pagination handlers
    application.add_handler(CallbackQueryHandler(list_projects, pattern="^list_projects:\d+$"))
    application.add_handler(CallbackQueryHandler(list_tasks, pattern="^list_tasks_(all|my):\d+$"))
    application.add_handler(CallbackQueryHandler(list_meetings, pattern="^list_meetings:\d+$"))

    # Error handler (must be added last)
    application.add_error_handler(error_handler)

    return application


# Create the application instance
application = create_bot_application()

