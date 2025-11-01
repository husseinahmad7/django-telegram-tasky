"""
Bot configuration for core_meetings app.
Defines handlers for meeting management.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from core_bot.utils import MessageFormatter

# App metadata
APP_NAME = "Meetings"
APP_EMOJI = "📅"
APP_DESCRIPTION = "Meeting scheduling and management"
APP_ORDER = 3  # Order in menu

# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="list_meetings"
        )
    ]

# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers.meetings import (
        list_meetings, schedule_meeting, meeting_detail,
        meeting_title_received, meeting_desc_received,
        meeting_project_received, meeting_time_received,
        meeting_vote, submit_vote, view_meeting_votes,
        cancel_meeting_creation,
        MEETING_TITLE, MEETING_DESC, MEETING_PROJECT, MEETING_TIME
    )
    
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
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(list_meetings, pattern="^list_meetings"))
    application.add_handler(CallbackQueryHandler(meeting_detail, pattern=r"^meeting:\d+$"))
    application.add_handler(CallbackQueryHandler(meeting_vote, pattern="^vote_meeting:"))
    application.add_handler(CallbackQueryHandler(submit_vote, pattern="^vote_submit:"))
    application.add_handler(CallbackQueryHandler(view_meeting_votes, pattern="^meeting_votes:"))
    
    # Pagination handlers
    application.add_handler(CallbackQueryHandler(list_meetings, pattern=r"^list_meetings:\d+$"))

# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} Meetings:</b>
/meetings - List upcoming meetings
/schedulemeeting - Schedule new meeting
/meetingvote [meeting_id] - Vote on meeting time
"""

