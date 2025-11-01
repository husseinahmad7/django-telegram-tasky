"""
Bot configuration for core_approvals app.
Defines handlers for approval workflows.
"""
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from core_bot.utils import MessageFormatter

# App metadata
APP_NAME = "Approvals"
APP_EMOJI = "✔️"
APP_DESCRIPTION = "Approval workflows and requests"
APP_ORDER = 4  # Order in menu

# Menu configuration
def get_menu_buttons():
    """Return menu buttons for this app."""
    from telegram import InlineKeyboardButton
    return [
        InlineKeyboardButton(
            f"{APP_EMOJI} {APP_NAME}",
            callback_data="list_approvals"
        )
    ]

# Handler registration
def register_handlers(application):
    """Register all handlers for this app."""
    from .handlers.approvals import (
        list_approvals, approval_detail, request_approval,
        approval_type_received, approval_item_received,
        approval_reason_received, approve_action, reject_action,
        cancel_approval_request, approve_task, reject_task,
        APPROVAL_TYPE, APPROVAL_ITEM, APPROVAL_REASON
    )
    
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
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(list_approvals, pattern="^list_approvals"))
    application.add_handler(CallbackQueryHandler(approval_detail, pattern=r"^approval:\d+$"))
    application.add_handler(CallbackQueryHandler(approve_action, pattern="^approve_action:"))
    application.add_handler(CallbackQueryHandler(reject_action, pattern="^reject_action:"))

# Help text for this app
def get_help_text():
    """Return help text for this app."""
    return f"""
<b>{APP_EMOJI} Approvals:</b>
/approvals - Pending approvals
/approve [id] - Approve request
/reject [id] - Reject request
"""

