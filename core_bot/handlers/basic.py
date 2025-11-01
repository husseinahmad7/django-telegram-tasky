"""
Basic bot commands: start, help, menu.
"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from core_bot.utils import get_or_create_user, KeyboardBuilder, MessageFormatter


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - welcome message and main menu."""
    user = await get_or_create_user(update, context)
    
    if not user:
        await update.message.reply_text("Sorry, I couldn't identify you. Please try again.")
        return
    
    welcome_msg = f"""
{MessageFormatter.EMOJI['success']} <b>Welcome to Tasky Project Manager!</b>

Hello {user.telegram_name}! 👋

I'm your personal project management assistant. I can help you:

{MessageFormatter.EMOJI['project']} Manage projects and tasks
{MessageFormatter.EMOJI['user']} Assign and track work
{MessageFormatter.EMOJI['deadline']} Set and monitor deadlines
{MessageFormatter.EMOJI['meeting']} Schedule meetings and votes
{MessageFormatter.EMOJI['report']} Generate daily/weekly reports
{MessageFormatter.EMOJI['approval']} Handle approvals and alerts
{MessageFormatter.EMOJI['resource']} Share learning resources

Use /menu to see all available commands or /help for detailed information.
"""
    
    buttons = [
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['project']} My Projects", callback_data="my_projects")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['task']} My Tasks", callback_data="my_tasks")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['meeting']} Meetings", callback_data="list_meetings")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['alert']} Notifications", callback_data="notifications")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['info']} Help", callback_data="help")],
    ]

    keyboard = InlineKeyboardMarkup(buttons)
    
    await update.message.reply_text(
        welcome_msg,
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - show all available commands."""
    help_text = f"""
{MessageFormatter.EMOJI['info']} <b>Tasky Bot Commands</b>

<b>📁 Project Management:</b>
/projects - List all projects
/myprojects - Your projects
/createproject - Create new project
/project [id] - View project details

<b>📝 Task Management:</b>
/tasks - List all tasks
/mytasks - Your assigned tasks
/createtask - Create new task
/task [id] - View task details
/assign [task_id] [user] - Assign task
/status [task_id] [status] - Update task status

<b>📊 Reports:</b>
/dailyreport - Submit daily report
/weeklyreport - View weekly summary
/progress [project_id] - Project progress

<b>📅 Meetings:</b>
/meetings - List upcoming meetings
/schedulemeeting - Schedule new meeting
/meetingvote [meeting_id] - Vote on meeting time

<b>✔️ Approvals:</b>
/approvals - Pending approvals
/approve [id] - Approve request
/reject [id] - Reject request

<b>🔔 Notifications:</b>
/notifications - View all notifications
/settings - Notification preferences

<b>📚 Resources:</b>
/resources [project_id] - Learning resources
/addresource - Add new resource

<b>⚙️ Settings:</b>
/settings - User preferences
/timezone [tz] - Set timezone
/language [lang] - Set language

Use inline buttons for easier navigation!
"""
    
    back_button = [[KeyboardBuilder.back_button("menu")]]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=back_button)
    
    if update.message:
        await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(help_text, parse_mode='HTML', reply_markup=keyboard)


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main menu."""
    user = await get_or_create_user(update, context)
    
    menu_text = f"""
{MessageFormatter.EMOJI['project']} <b>Main Menu</b>

What would you like to do, {user.telegram_name}?
"""
    
    buttons = [
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['project']} Projects", callback_data="list_projects"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['task']} Tasks", callback_data="list_tasks"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['meeting']} Meetings", callback_data="list_meetings"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['report']} Reports", callback_data="reports_menu"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['approval']} Approvals", callback_data="approvals_menu"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['alert']} Notifications", callback_data="notifications"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['resource']} Resources", callback_data="resources_menu"),
        InlineKeyboardButton(f"{MessageFormatter.EMOJI['user']} Settings", callback_data="settings"),
    ]
    
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=2)
    
    if update.message:
        await update.message.reply_text(menu_text, parse_mode='HTML', reply_markup=keyboard)
    elif update.callback_query:
        await update.callback_query.edit_message_text(menu_text, parse_mode='HTML', reply_markup=keyboard)

