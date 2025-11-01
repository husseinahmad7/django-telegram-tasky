"""
Notification and reminder handlers.
"""
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes
from core_bot.utils import (
    get_or_create_user, ModelManager, KeyboardBuilder,
    MessageFormatter, paginate_items
)


async def list_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List user notifications."""
    user = await get_or_create_user(update, context)
    
    page = 0
    if update.callback_query and ':' in update.callback_query.data:
        page = int(update.callback_query.data.split(':')[1])
    
    alert_manager = ModelManager('core_tasks', 'Alert')
    all_alerts = await alert_manager.filter(user_id=user.id)
    
    # Sort by created_at descending
    all_alerts.sort(key=lambda a: a.created_at, reverse=True)
    
    if not all_alerts:
        msg = f"{MessageFormatter.EMOJI['alert']} <b>Notifications</b>\n\n"
        msg += "No notifications.\n\n"
        msg += "You're all caught up! ✅"
        
        buttons = [[KeyboardBuilder.back_button("menu")]]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
        
        if update.message:
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    paginated = paginate_items(all_alerts, page=page, per_page=5)
    
    unread_count = len([a for a in all_alerts if not a.is_read])
    
    msg = f"{MessageFormatter.EMOJI['alert']} <b>Notifications</b>\n"
    msg += f"Unread: {unread_count} | Total: {paginated['total_items']}\n\n"
    
    buttons = []
    for alert in paginated['items']:
        read_emoji = "📭" if alert.is_read else "📬"
        alert_type_emoji = {
            'TASK_ASSIGNED': '📝',
            'DEADLINE': '⏰',
            'OVERDUE': '⚠️',
            'MEETING': '📅',
            'APPROVAL': '✅',
            'GENERAL': '📢'
        }.get(alert.alert_type, '📢')
        
        date_str = alert.created_at.strftime('%m/%d %H:%M')
        button_text = f"{read_emoji} {alert_type_emoji} {alert.alert_type.replace('_', ' ').title()} - {date_str}"
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"notification:{alert.id}"))
    
    footer_buttons = []
    
    if unread_count > 0:
        footer_buttons.append([InlineKeyboardButton("✅ Mark All Read", callback_data="mark_all_read")])
    
    if paginated['total_pages'] > 1:
        footer_buttons.append(
            KeyboardBuilder.pagination_buttons(
                paginated['current_page'],
                paginated['total_pages'],
                "notifications"
            )
        )
    
    footer_buttons.append([KeyboardBuilder.back_button("menu")])
    
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1, footer_buttons=footer_buttons)
    
    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def notification_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show notification details."""
    query = update.callback_query
    await query.answer()
    
    alert_id = int(query.data.split(':')[1])
    
    alert_manager = ModelManager('core_tasks', 'Alert')
    alert = await alert_manager.get(id=alert_id)
    
    if not alert:
        await query.edit_message_text("Notification not found.")
        return
    
    # Mark as read
    if not alert.is_read:
        await alert_manager.update(alert_id, is_read=True)
    
    alert_type_emoji = {
        'TASK_ASSIGNED': '📝',
        'DEADLINE': '⏰',
        'OVERDUE': '⚠️',
        'MEETING': '📅',
        'APPROVAL': '✅',
        'GENERAL': '📢'
    }.get(alert.alert_type, '📢')
    
    msg = f"{alert_type_emoji} <b>{alert.alert_type.replace('_', ' ').title()}</b>\n\n"
    msg += f"{alert.message}\n\n"
    msg += f"<b>Time:</b> {alert.created_at.strftime('%Y-%m-%d %H:%M')}\n"
    
    if alert.task:
        msg += f"<b>Task:</b> {alert.task.title}\n"
    elif alert.project:
        msg += f"<b>Project:</b> {alert.project.name}\n"
    
    buttons = []
    
    # Add action buttons based on alert type
    if alert.task:
        buttons.append([InlineKeyboardButton("View Task", callback_data=f"task:{alert.task.id}")])
    elif alert.project:
        buttons.append([InlineKeyboardButton("View Project", callback_data=f"project:{alert.project.id}")])
    
    buttons.append([KeyboardBuilder.back_button("notifications:0")])
    
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def mark_all_read(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark all notifications as read."""
    query = update.callback_query
    await query.answer()
    
    user = await get_or_create_user(update, context)
    
    alert_manager = ModelManager('core_tasks', 'Alert')
    unread_alerts = await alert_manager.filter(user_id=user.id, is_read=False)
    
    for alert in unread_alerts:
        await alert_manager.update(alert.id, is_read=True)
    
    msg = f"{MessageFormatter.EMOJI['success']} All notifications marked as read!"
    
    buttons = [[KeyboardBuilder.back_button("notifications:0")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List user reminders."""
    user = await get_or_create_user(update, context)
    
    reminder_manager = ModelManager('core_tasks', 'Reminder')
    all_reminders = await reminder_manager.filter(user_id=user.id, is_sent=False)
    
    # Sort by reminder_time
    all_reminders.sort(key=lambda r: r.reminder_time)
    
    if not all_reminders:
        msg = f"{MessageFormatter.EMOJI['deadline']} <b>Upcoming Reminders</b>\n\n"
        msg += "No upcoming reminders."
        
        buttons = [[KeyboardBuilder.back_button("menu")]]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
        
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    msg = f"{MessageFormatter.EMOJI['deadline']} <b>Upcoming Reminders</b>\n"
    msg += f"Total: {len(all_reminders)}\n\n"
    
    for reminder in all_reminders[:10]:  # Show first 10
        time_str = reminder.reminder_time.strftime('%m/%d %H:%M')
        reminder_type_emoji = {
            'DEADLINE': '⏰',
            'MEETING': '📅',
            'DAILY_REPORT': '📊',
            'CUSTOM': '🔔'
        }.get(reminder.reminder_type, '🔔')
        
        msg += f"{reminder_type_emoji} <b>{time_str}</b>\n"
        msg += f"   {reminder.message}\n\n"
    
    if len(all_reminders) > 10:
        msg += f"... and {len(all_reminders) - 10} more"
    
    buttons = [[KeyboardBuilder.back_button("menu")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
    
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def notification_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show notification settings."""
    user = await get_or_create_user(update, context)
    
    msg = f"{MessageFormatter.EMOJI['settings']} <b>Notification Settings</b>\n\n"
    msg += "Configure your notification preferences:\n\n"
    
    settings_list = [
        ('Task Assigned', user.notify_task_assigned, 'task_assigned'),
        ('Deadline Approaching', user.notify_deadline_approaching, 'deadline'),
        ('Meeting Scheduled', user.notify_meeting_scheduled, 'meeting'),
        ('Approval Required', user.notify_approval_required, 'approval'),
    ]
    
    buttons = []
    for label, enabled, key in settings_list:
        status = "✅" if enabled else "❌"
        msg += f"{status} {label}\n"
        toggle_text = f"{'Disable' if enabled else 'Enable'} {label}"
        buttons.append(InlineKeyboardButton(toggle_text, callback_data=f"toggle_notif:{key}"))
    
    buttons.append(KeyboardBuilder.back_button("menu"))
    
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1)
    
    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Toggle notification setting."""
    query = update.callback_query
    await query.answer()
    
    user = await get_or_create_user(update, context)
    setting_key = query.data.split(':')[1]
    
    user_manager = ModelManager('core_auth', 'TelegramUser')
    
    field_map = {
        'task_assigned': 'notify_task_assigned',
        'deadline': 'notify_deadline_approaching',
        'meeting': 'notify_meeting_scheduled',
        'approval': 'notify_approval_required',
    }
    
    field_name = field_map.get(setting_key)
    if field_name:
        current_value = getattr(user, field_name)
        await user_manager.update(user.id, **{field_name: not current_value})
    
    # Refresh settings view
    await notification_settings(update, context)

