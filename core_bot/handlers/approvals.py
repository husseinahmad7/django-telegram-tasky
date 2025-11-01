"""
Approval workflow handlers.
"""
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from core_bot.utils import (
    get_or_create_user, ModelManager, KeyboardBuilder,
    MessageFormatter, paginate_items
)
from datetime import datetime


# Conversation states
APPROVAL_TYPE, APPROVAL_ITEM, APPROVAL_REASON = range(3)


async def list_approvals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List pending approvals."""
    user = await get_or_create_user(update, context)

    page = 0
    if update.callback_query and ':' in update.callback_query.data:
        page = int(update.callback_query.data.split(':')[1])

    approval_manager = ModelManager('core_tasks', 'Approval')

    # Get pending approvals for this user
    all_approvals = await approval_manager.filter(approver_id=user.id, status='PENDING')

    if not all_approvals:
        msg = f"{MessageFormatter.EMOJI['approval']} <b>Pending Approvals</b>\n\n"
        msg += "No pending approvals.\n\n"
        msg += "You're all caught up! ✅"

        buttons = [[KeyboardBuilder.back_button("menu")]]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

        if update.message:
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return

    paginated = paginate_items(all_approvals, page=page, per_page=5)

    msg = f"{MessageFormatter.EMOJI['approval']} <b>Pending Approvals</b>\n"
    msg += f"Showing {len(paginated['items'])} of {paginated['total_items']} approvals\n\n"

    buttons = []
    for approval in paginated['items']:
        created_date = approval.created_at.strftime('%m/%d')
        button_text = f"📋 {approval.approval_type.title()} - {created_date}"
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"approval:{approval.id}"))

    footer_buttons = []
    if paginated['total_pages'] > 1:
        footer_buttons.append(
            KeyboardBuilder.pagination_buttons(
                paginated['current_page'],
                paginated['total_pages'],
                "list_approvals"
            )
        )

    footer_buttons.append([KeyboardBuilder.back_button("menu")])

    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1, footer_buttons=footer_buttons)

    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def approval_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show approval details."""
    query = update.callback_query
    await query.answer()

    approval_id = int(query.data.split(':')[1])

    approval_manager = ModelManager('core_tasks', 'Approval')
    approval = await approval_manager.get(id=approval_id)

    if not approval:
        await query.edit_message_text("Approval not found.")
        return

    msg = f"{MessageFormatter.EMOJI['approval']} <b>Approval Request</b>\n\n"
    msg += f"<b>Type:</b> {approval.approval_type.title()}\n"
    msg += f"<b>Status:</b> {approval.status}\n"

    # Get task or project name (avoid ForeignKey access in async context)
    if approval.task_id:
        task_manager = ModelManager('core_tasks', 'Task')
        task = await task_manager.get(id=approval.task_id)
        if task:
            msg += f"<b>Task:</b> {task.title}\n"
    elif approval.project_id:
        project_manager = ModelManager('core_tasks', 'Project')
        project = await project_manager.get(id=approval.project_id)
        if project:
            msg += f"<b>Project:</b> {project.name}\n"

    msg += f"<b>Requested by:</b> {approval.requested_by.telegram_name or approval.requested_by.username}\n"
    msg += f"<b>Requested:</b> {approval.created_at.strftime('%Y-%m-%d %H:%M')}\n"

    if approval.reason:
        msg += f"\n<b>Reason:</b>\n{approval.reason}\n"

    if approval.status == 'PENDING':
        buttons = [
            [InlineKeyboardButton("✅ Approve", callback_data=f"approve_action:{approval_id}")],
            [InlineKeyboardButton("❌ Reject", callback_data=f"reject_action:{approval_id}")],
            [KeyboardBuilder.back_button("list_approvals:0")],
        ]
    else:
        if approval.approved_at:
            msg += f"\n<b>Decided:</b> {approval.approved_at.strftime('%Y-%m-%d %H:%M')}\n"
        if approval.approval_notes:
            msg += f"<b>Notes:</b> {approval.approval_notes}\n"

        buttons = [[KeyboardBuilder.back_button("list_approvals:0")]]

    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def request_approval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start approval request conversation."""
    msg = f"{MessageFormatter.EMOJI['approval']} <b>Request Approval</b>\n\n"
    msg += "Select approval type:"

    buttons = [
        [InlineKeyboardButton("📝 Task Approval", callback_data="approval_type:task")],
        [InlineKeyboardButton("📁 Project Approval", callback_data="approval_type:project")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="menu")],
    ]

    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)

    return APPROVAL_TYPE


async def approval_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive approval type."""
    query = update.callback_query
    await query.answer()

    approval_type = query.data.split(':')[1]
    context.user_data['approval_type'] = approval_type

    if approval_type == 'task':
        # Get user's tasks
        user = await get_or_create_user(update, context)
        task_manager = ModelManager('core_tasks', 'Task')
        tasks = await task_manager.filter(assigned_to_id=user.id, status__in=['DONE', 'REVIEW'])

        if not tasks:
            await query.edit_message_text(
                "You don't have any completed or in-review tasks to request approval for."
            )
            return ConversationHandler.END

        buttons = []
        for task in tasks[:10]:  # Limit to 10
            buttons.append(InlineKeyboardButton(
                f"{task.title} ({task.status})",
                callback_data=f"approval_item:task:{task.id}"
            ))

        msg = "Select task for approval:"

    else:  # project
        project_manager = ModelManager('core_tasks', 'Project')
        projects = await project_manager.all()

        if not projects:
            await query.edit_message_text("No projects available.")
            return ConversationHandler.END

        buttons = []
        for project in projects[:10]:
            buttons.append(InlineKeyboardButton(
                project.name,
                callback_data=f"approval_item:project:{project.id}"
            ))

        msg = "Select project for approval:"

    buttons.append(InlineKeyboardButton("🔙 Cancel", callback_data="cancel_approval"))
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1)

    await query.edit_message_text(msg, reply_markup=keyboard)

    return APPROVAL_ITEM


async def approval_item_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive approval item."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split(':')
    item_type = parts[1]
    item_id = int(parts[2])

    context.user_data['approval_item_type'] = item_type
    context.user_data['approval_item_id'] = item_id

    msg = "Enter reason for approval request (or /skip):"
    await query.edit_message_text(msg)

    return APPROVAL_REASON


async def approval_reason_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive approval reason and create approval request."""
    user = await get_or_create_user(update, context)

    reason = update.message.text if update.message.text != '/skip' else ''

    # Get project owner or manager as approver
    item_type = context.user_data['approval_item_type']
    item_id = context.user_data['approval_item_id']

    if item_type == 'task':
        task_manager = ModelManager('core_tasks', 'Task')
        task = await task_manager.get(id=item_id)

        # Get project owner (avoid ForeignKey access in async context)
        approver_id = user.id  # Default to self
        if task and task.project_id:
            project_manager = ModelManager('core_tasks', 'Project')
            project = await project_manager.get(id=task.project_id)
            if project:
                approver_id = project.owner_id

        approval_data = {
            'approval_type': 'TASK',
            'task_id': item_id,
            'requested_by_id': user.id,
            'approver_id': approver_id,
            'reason': reason,
            'status': 'PENDING'
        }
    else:  # project
        project_manager = ModelManager('core_tasks', 'Project')
        project = await project_manager.get(id=item_id)
        approver_id = project.owner_id if project else user.id

        approval_data = {
            'approval_type': 'PROJECT',
            'project_id': item_id,
            'requested_by_id': user.id,
            'approver_id': approver_id,
            'reason': reason,
            'status': 'PENDING'
        }

    approval_manager = ModelManager('core_tasks', 'Approval')
    approval = await approval_manager.create(**approval_data)

    msg = f"{MessageFormatter.EMOJI['success']} Approval request submitted!\n\n"
    msg += f"Type: {approval.approval_type}\n"
    msg += "The approver will be notified."

    await update.message.reply_text(msg, parse_mode='HTML')

    context.user_data.clear()
    return ConversationHandler.END


async def approve_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve an approval request."""
    query = update.callback_query
    await query.answer()

    approval_id = int(query.data.split(':')[1])

    approval_manager = ModelManager('core_tasks', 'Approval')
    approval = await approval_manager.update(
        approval_id,
        status='APPROVED',
        approved_at=datetime.now()
    )

    msg = f"{MessageFormatter.EMOJI['success']} <b>Approved!</b>\n\n"
    msg += "The approval request has been approved."

    buttons = [[KeyboardBuilder.back_button("list_approvals:0")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def reject_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject an approval request."""
    query = update.callback_query
    await query.answer()

    approval_id = int(query.data.split(':')[1])

    approval_manager = ModelManager('core_tasks', 'Approval')
    approval = await approval_manager.update(
        approval_id,
        status='REJECTED',
        approved_at=datetime.now()
    )

    msg = f"{MessageFormatter.EMOJI['error']} <b>Rejected</b>\n\n"
    msg += "The approval request has been rejected."

    buttons = [[KeyboardBuilder.back_button("list_approvals:0")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def cancel_approval_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel approval request."""
    query = update.callback_query
    await query.answer()

    context.user_data.clear()

    msg = f"{MessageFormatter.EMOJI['info']} Approval request cancelled."
    await query.edit_message_text(msg, parse_mode='HTML')

    return ConversationHandler.END


# Keep old function names for compatibility
async def approve_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Approve a task - redirect to list approvals."""
    await list_approvals(update, context)


async def reject_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Reject a task - redirect to list approvals."""
    await list_approvals(update, context)

