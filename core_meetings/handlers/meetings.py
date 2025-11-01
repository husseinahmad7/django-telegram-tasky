"""
Meeting management handlers.
"""
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from core_bot.utils import (
    get_or_create_user, ModelManager, KeyboardBuilder,
    MessageFormatter, paginate_items
)
from datetime import datetime, timedelta


# Conversation states
MEETING_TITLE, MEETING_DESC, MEETING_PROJECT, MEETING_TIME = range(4)


async def list_meetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List upcoming meetings."""
    user = await get_or_create_user(update, context)

    page = 0
    if update.callback_query and ':' in update.callback_query.data:
        page = int(update.callback_query.data.split(':')[1])

    meeting_manager = ModelManager('core_tasks', 'Meeting')
    all_meetings = await meeting_manager.filter(scheduled_at__gte=datetime.now())

    # Sort by scheduled time
    all_meetings.sort(key=lambda m: m.scheduled_at)

    if not all_meetings:
        msg = f"{MessageFormatter.EMOJI['meeting']} <b>Upcoming Meetings</b>\n\n"
        msg += "No upcoming meetings scheduled.\n\n"
        msg += "Use /schedulemeeting to create one!"

        buttons = [
            [InlineKeyboardButton("➕ Schedule Meeting", callback_data="schedule_meeting")],
            [KeyboardBuilder.back_button("menu")]
        ]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

        if update.message:
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return

    paginated = paginate_items(all_meetings, page=page, per_page=5)

    msg = f"{MessageFormatter.EMOJI['meeting']} <b>Upcoming Meetings</b>\n"
    msg += f"Showing {len(paginated['items'])} of {paginated['total_items']} meetings\n\n"

    buttons = []
    for meeting in paginated['items']:
        time_str = meeting.scheduled_at.strftime('%m/%d %H:%M')
        button_text = f"📅 {meeting.title} - {time_str}"
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"meeting:{meeting.id}"))

    footer_buttons = []
    if paginated['total_pages'] > 1:
        footer_buttons.append(
            KeyboardBuilder.pagination_buttons(
                paginated['current_page'],
                paginated['total_pages'],
                "list_meetings"
            )
        )

    footer_buttons.append([InlineKeyboardButton("➕ Schedule Meeting", callback_data="schedule_meeting")])
    footer_buttons.append([KeyboardBuilder.back_button("menu")])

    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1, footer_buttons=footer_buttons)

    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def meeting_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show meeting details."""
    query = update.callback_query
    await query.answer()

    meeting_id = int(query.data.split(':')[1])

    meeting_manager = ModelManager('core_tasks', 'Meeting')
    meeting = await meeting_manager.get(id=meeting_id)

    if not meeting:
        await query.edit_message_text("Meeting not found.")
        return

    msg = f"{MessageFormatter.EMOJI['meeting']} <b>{meeting.title}</b>\n\n"

    if meeting.description:
        msg += f"{meeting.description}\n\n"

    msg += f"<b>📅 Time:</b> {meeting.scheduled_at.strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"<b>⏱️ Duration:</b> {meeting.duration_minutes} minutes\n"

    # Get project name if linked (avoid accessing ForeignKey in async context)
    if meeting.project_id:
        project_manager = ModelManager('core_tasks', 'Project')
        project = await project_manager.get(id=meeting.project_id)
        if project:
            msg += f"<b>📁 Project:</b> {project.name}\n"

    if meeting.location:
        msg += f"<b>📍 Location:</b> {meeting.location}\n"

    if meeting.meeting_link:
        msg += f"<b>🔗 Link:</b> {meeting.meeting_link}\n"

    # Get vote count
    vote_manager = ModelManager('core_tasks', 'MeetingVote')
    votes = await vote_manager.filter(meeting_id=meeting_id)

    msg += f"\n<b>👥 Votes:</b> {len(votes)}\n"

    buttons = [
        [InlineKeyboardButton("✅ Vote Available", callback_data=f"vote_meeting:{meeting_id}")],
        [InlineKeyboardButton("📊 View Votes", callback_data=f"meeting_votes:{meeting_id}")],
        [KeyboardBuilder.back_button("list_meetings:0")],
    ]

    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def schedule_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start meeting scheduling conversation."""
    if update.callback_query:
        await update.callback_query.answer()
        msg = f"{MessageFormatter.EMOJI['meeting']} <b>Schedule New Meeting</b>\n\nEnter meeting title:"
        await update.callback_query.edit_message_text(msg, parse_mode='HTML')
    else:
        msg = f"{MessageFormatter.EMOJI['meeting']} <b>Schedule New Meeting</b>\n\nEnter meeting title:"
        await update.message.reply_text(msg, parse_mode='HTML')

    return MEETING_TITLE


async def meeting_title_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive meeting title."""
    context.user_data['meeting_title'] = update.message.text

    msg = "Enter meeting description (or /skip):"
    await update.message.reply_text(msg)

    return MEETING_DESC


async def meeting_desc_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive meeting description."""
    if update.message.text != '/skip':
        context.user_data['meeting_desc'] = update.message.text
    else:
        context.user_data['meeting_desc'] = ''

    # Get projects for selection
    project_manager = ModelManager('core_tasks', 'Project')
    projects = await project_manager.all()

    if not projects:
        context.user_data['meeting_project_id'] = None
        msg = "Enter meeting time (YYYY-MM-DD HH:MM):"
        await update.message.reply_text(msg)
        return MEETING_TIME

    buttons = []
    for project in projects[:10]:  # Limit to 10 projects
        buttons.append(InlineKeyboardButton(project.name, callback_data=f"meeting_project:{project.id}"))

    buttons.append(InlineKeyboardButton("⏭️ Skip (No Project)", callback_data="meeting_project:none"))

    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1)

    msg = "Select project (optional):"
    await update.message.reply_text(msg, reply_markup=keyboard)

    return MEETING_PROJECT


async def meeting_project_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive meeting project."""
    query = update.callback_query
    await query.answer()

    project_id = query.data.split(':')[1]

    if project_id == 'none':
        context.user_data['meeting_project_id'] = None
    else:
        context.user_data['meeting_project_id'] = int(project_id)

    msg = "Enter meeting time (YYYY-MM-DD HH:MM):"
    await query.edit_message_text(msg)

    return MEETING_TIME


async def meeting_time_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive meeting time and create meeting."""
    user = await get_or_create_user(update, context)

    try:
        scheduled_time = datetime.strptime(update.message.text, '%Y-%m-%d %H:%M')
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid date format. Please use YYYY-MM-DD HH:MM\n"
            "Example: 2024-12-25 14:30"
        )
        return MEETING_TIME

    # Create meeting
    meeting_manager = ModelManager('core_tasks', 'Meeting')
    meeting = await meeting_manager.create(
        title=context.user_data['meeting_title'],
        description=context.user_data.get('meeting_desc', ''),
        project_id=context.user_data.get('meeting_project_id'),
        scheduled_at=scheduled_time,
        duration_minutes=60,  # Default 1 hour
        organizer_id=user.id
    )

    msg = f"{MessageFormatter.EMOJI['success']} Meeting scheduled successfully!\n\n"
    msg += f"<b>📅 {meeting.title}</b>\n"
    msg += f"<b>Time:</b> {meeting.scheduled_at.strftime('%Y-%m-%d %H:%M')}\n"
    msg += f"<b>Duration:</b> {meeting.duration_minutes} minutes\n"

    buttons = [
        [InlineKeyboardButton("View Meeting", callback_data=f"meeting:{meeting.id}")],
        [KeyboardBuilder.back_button("list_meetings:0")],
    ]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)

    context.user_data.clear()
    return ConversationHandler.END


async def meeting_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Vote on meeting availability."""
    query = update.callback_query
    await query.answer()

    meeting_id = int(query.data.split(':')[1])
    user = await get_or_create_user(update, context)

    # Check if already voted
    vote_manager = ModelManager('core_tasks', 'MeetingVote')
    existing_vote = await vote_manager.filter(meeting_id=meeting_id, user_id=user.id)

    if existing_vote:
        msg = "You've already voted for this meeting!\n\nChange your vote:"
    else:
        msg = "Vote for this meeting time:"

    buttons = [
        [InlineKeyboardButton("✅ Available", callback_data=f"vote_submit:{meeting_id}:available")],
        [InlineKeyboardButton("❌ Not Available", callback_data=f"vote_submit:{meeting_id}:not_available")],
        [InlineKeyboardButton("❓ Maybe", callback_data=f"vote_submit:{meeting_id}:maybe")],
        [KeyboardBuilder.back_button(f"meeting:{meeting_id}")],
    ]

    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, reply_markup=keyboard)


async def submit_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Submit meeting vote."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split(':')
    meeting_id = int(parts[1])
    vote_type = parts[2]

    user = await get_or_create_user(update, context)

    vote_manager = ModelManager('core_tasks', 'MeetingVote')

    # Check if already voted
    existing_votes = await vote_manager.filter(meeting_id=meeting_id, user_id=user.id)

    if existing_votes:
        # Update existing vote
        await vote_manager.update(existing_votes[0].id, vote=vote_type)
        msg = f"{MessageFormatter.EMOJI['success']} Vote updated!"
    else:
        # Create new vote
        await vote_manager.create(
            meeting_id=meeting_id,
            user_id=user.id,
            vote=vote_type
        )
        msg = f"{MessageFormatter.EMOJI['success']} Vote submitted!"

    # Show meeting detail again
    context.user_data['temp_meeting_id'] = meeting_id
    await query.edit_message_text(msg, parse_mode='HTML')

    # Redirect to meeting detail
    await meeting_detail(update, context)


async def view_meeting_votes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View all votes for a meeting."""
    query = update.callback_query
    await query.answer()

    meeting_id = int(query.data.split(':')[1])

    vote_manager = ModelManager('core_tasks', 'MeetingVote')
    votes = await vote_manager.filter(meeting_id=meeting_id)

    if not votes:
        msg = f"{MessageFormatter.EMOJI['info']} No votes yet for this meeting."
    else:
        available = len([v for v in votes if v.vote == 'available'])
        not_available = len([v for v in votes if v.vote == 'not_available'])
        maybe = len([v for v in votes if v.vote == 'maybe'])

        msg = f"{MessageFormatter.EMOJI['chart']} <b>Meeting Votes</b>\n\n"
        msg += f"✅ Available: {available}\n"
        msg += f"❌ Not Available: {not_available}\n"
        msg += f"❓ Maybe: {maybe}\n"
        msg += f"\n<b>Total:</b> {len(votes)} votes"

    buttons = [[KeyboardBuilder.back_button(f"meeting:{meeting_id}")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)

    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def cancel_meeting_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel meeting creation."""
    context.user_data.clear()
    await update.message.reply_text(
        f"{MessageFormatter.EMOJI['info']} Meeting creation cancelled.",
        parse_mode='HTML'
    )
    return ConversationHandler.END

