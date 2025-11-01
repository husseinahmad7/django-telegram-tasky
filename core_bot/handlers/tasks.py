"""
Task management handlers.
"""
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from core_bot.utils import (
    get_or_create_user, ModelManager, KeyboardBuilder,
    MessageFormatter, paginate_items
)
from datetime import datetime, timedelta


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List tasks with filters."""
    user = await get_or_create_user(update, context)
    
    page = 0
    filter_type = 'all'  # all, my, project
    
    if update.callback_query and ':' in update.callback_query.data:
        parts = update.callback_query.data.split(':')
        if len(parts) > 1:
            filter_type = parts[0].replace('list_tasks_', '')
            page = int(parts[1]) if len(parts) > 2 else 0
    
    task_manager = ModelManager('core_tasks', 'Task')
    
    if filter_type == 'my':
        all_tasks = await task_manager.filter(assigned_to_id=user.id)
    else:
        all_tasks = await task_manager.all()
    
    # Sort by priority and deadline
    all_tasks.sort(key=lambda t: (t.priority != 'URGENT', t.priority != 'HIGH', t.deadline or datetime.max))
    
    if not all_tasks:
        msg = f"{MessageFormatter.EMOJI['info']} No tasks found."
        buttons = [[KeyboardBuilder.back_button("menu")]]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
        
        if update.message:
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    paginated = paginate_items(all_tasks, page=page, per_page=5)
    
    msg = f"{MessageFormatter.EMOJI['task']} <b>Tasks</b>\n"
    msg += f"Showing {len(paginated['items'])} of {paginated['total_items']} tasks\n\n"
    
    buttons = []
    for task in paginated['items']:
        status_emoji = MessageFormatter.get_status_emoji(task.status)
        priority_emoji = MessageFormatter.get_priority_emoji(task.priority)
        
        button_text = f"{status_emoji}{priority_emoji} {task.title[:30]}"
        if task.is_overdue:
            button_text += " ⚠️"
        
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"task:{task.id}"))
    
    footer_buttons = []
    if paginated['total_pages'] > 1:
        footer_buttons.append(
            KeyboardBuilder.pagination_buttons(
                paginated['current_page'],
                paginated['total_pages'],
                f"list_tasks_{filter_type}"
            )
        )
    
    footer_buttons.append([
        InlineKeyboardButton("📋 All", callback_data="list_tasks_all:0"),
        InlineKeyboardButton("👤 My Tasks", callback_data="list_tasks_my:0"),
    ])
    footer_buttons.append([KeyboardBuilder.back_button("menu")])
    
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1, footer_buttons=footer_buttons)

    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        # Try to edit message, but catch "message not modified" error
        try:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        except Exception as e:
            # If message is not modified, just answer the callback query
            if "message is not modified" in str(e).lower():
                await update.callback_query.answer("Already showing this view")
            else:
                raise


async def task_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show task details."""
    query = update.callback_query
    await query.answer()
    
    task_id = int(query.data.split(':')[1])
    
    task_manager = ModelManager('core_tasks', 'Task')
    task = await task_manager.get(id=task_id)
    
    if not task:
        await query.edit_message_text("Task not found.")
        return

    msg = MessageFormatter.format_task(task)

    # Get project name (avoid ForeignKey access in async context)
    if task.project_id:
        project_manager = ModelManager('core_tasks', 'Project')
        project = await project_manager.get(id=task.project_id)
        if project:
            msg += f"\n\n<b>Project:</b> {project.name}\n"

    msg += f"<b>Status:</b> {task.get_status_display()}\n"
    msg += f"<b>Created:</b> {task.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    
    if task.estimated_hours:
        msg += f"<b>Estimated:</b> {task.estimated_hours}h\n"
    if task.actual_hours:
        msg += f"<b>Actual:</b> {task.actual_hours}h\n"
    
    buttons = [
        [
            InlineKeyboardButton("✅ Done", callback_data=f"task_status:{task_id}:DONE"),
            InlineKeyboardButton("🔄 In Progress", callback_data=f"task_status:{task_id}:IN_PROGRESS"),
        ],
        [
            InlineKeyboardButton("👀 Review", callback_data=f"task_status:{task_id}:REVIEW"),
            InlineKeyboardButton("🚫 Blocked", callback_data=f"task_status:{task_id}:BLOCKED"),
        ],
        [InlineKeyboardButton("👤 Assign", callback_data=f"assign_task:{task_id}")],
        [InlineKeyboardButton("💬 Comments", callback_data=f"task_comments:{task_id}")],
        [KeyboardBuilder.back_button("list_tasks_all:0")],
    ]
    
    keyboard = KeyboardBuilder.build_menu([], n_cols=2, footer_buttons=buttons)
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def update_task_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Update task status."""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split(':')
    task_id = int(parts[1])
    new_status = parts[2]
    
    task_manager = ModelManager('core_tasks', 'Task')
    task = await task_manager.update(task_id, status=new_status)
    
    if task:
        msg = f"{MessageFormatter.EMOJI['success']} Task status updated to {task.get_status_display()}!"
        
        # Show task detail again
        await task_detail(update, context)
    else:
        await query.edit_message_text("Failed to update task status.")


# Conversation states
TASK_TITLE, TASK_DESC, TASK_PRIORITY, TASK_DEADLINE = range(4)


async def create_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start task creation."""
    if update.callback_query:
        await update.callback_query.answer()
        project_id = int(update.callback_query.data.split(':')[1])
        context.user_data['task_project_id'] = project_id
        
        msg = f"{MessageFormatter.EMOJI['task']} <b>Create New Task</b>\n\nEnter task title:"
        await update.callback_query.edit_message_text(msg, parse_mode='HTML')
    else:
        msg = f"{MessageFormatter.EMOJI['task']} <b>Create New Task</b>\n\nEnter task title:"
        await update.message.reply_text(msg, parse_mode='HTML')
    
    return TASK_TITLE


async def task_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive task title."""
    context.user_data['task_title'] = update.message.text
    
    msg = "Enter task description (or /skip):"
    await update.message.reply_text(msg)
    
    return TASK_DESC


async def task_desc_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive task description."""
    if update.message.text != '/skip':
        context.user_data['task_desc'] = update.message.text
    else:
        context.user_data['task_desc'] = ''
    
    buttons = [
        [InlineKeyboardButton("🟢 Low", callback_data="task_priority:LOW")],
        [InlineKeyboardButton("🟡 Medium", callback_data="task_priority:MEDIUM")],
        [InlineKeyboardButton("🔴 High", callback_data="task_priority:HIGH")],
        [InlineKeyboardButton("🚨 Urgent", callback_data="task_priority:URGENT")],
    ]
    keyboard = KeyboardBuilder.build_menu([], n_cols=2, footer_buttons=buttons)
    
    msg = "Select task priority:"
    await update.message.reply_text(msg, reply_markup=keyboard)
    
    return TASK_PRIORITY


async def task_priority_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive task priority."""
    query = update.callback_query
    await query.answer()
    
    priority = query.data.split(':')[1]
    context.user_data['task_priority'] = priority
    
    msg = "Enter deadline (YYYY-MM-DD HH:MM) or /skip:"
    await query.edit_message_text(msg)
    
    return TASK_DEADLINE


async def task_deadline_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive deadline and create task."""
    user = await get_or_create_user(update, context)

    deadline = None
    if update.message.text != '/skip':
        try:
            from django.utils import timezone as django_tz
            # Parse the datetime and make it timezone-aware
            naive_datetime = datetime.strptime(update.message.text, '%Y-%m-%d %H:%M')
            deadline = django_tz.make_aware(naive_datetime, django_tz.get_current_timezone())
        except ValueError:
            await update.message.reply_text("Invalid date format. Task created without deadline.")
    
    task_manager = ModelManager('core_tasks', 'Task')
    task = await task_manager.create(
        project_id=context.user_data['task_project_id'],
        title=context.user_data['task_title'],
        description=context.user_data.get('task_desc', ''),
        priority=context.user_data['task_priority'],
        deadline=deadline,
        created_by_id=user.id,
        status='TODO'
    )
    
    msg = f"{MessageFormatter.EMOJI['success']} Task created successfully!\n\n"
    msg += MessageFormatter.format_task(task)
    
    buttons = [
        [InlineKeyboardButton("View Task", callback_data=f"task:{task.id}")],
        [KeyboardBuilder.back_button("list_tasks_all:0")],
    ]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    
    context.user_data.clear()
    return ConversationHandler.END


async def assign_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Assign task to user."""
    # This would show a list of users to assign
    # For MVP, simplified version
    query = update.callback_query
    await query.answer()
    
    msg = "Task assignment feature - coming soon!\nUse admin panel to assign tasks for now."
    await query.edit_message_text(msg)

