"""
Project management handlers.
"""
from telegram import Update, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from core_bot.utils import (
    get_or_create_user, ModelManager, KeyboardBuilder,
    MessageFormatter, paginate_items
)


async def list_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all projects with pagination."""
    user = await get_or_create_user(update, context)
    
    # Get page number from callback data or default to 0
    page = 0
    if update.callback_query and ':' in update.callback_query.data:
        page = int(update.callback_query.data.split(':')[1])
    
    project_manager = ModelManager('core_tasks', 'Project')
    all_projects = await project_manager.all()
    
    if not all_projects:
        msg = f"{MessageFormatter.EMOJI['info']} No projects found.\n\nCreate your first project with /createproject"
        buttons = [[InlineKeyboardButton("➕ Create Project", callback_data="create_project")]]
        keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
        
        if update.message:
            await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
        else:
            await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
        return
    
    # Paginate projects
    paginated = paginate_items(all_projects, page=page, per_page=5)
    
    msg = f"{MessageFormatter.EMOJI['project']} <b>Projects</b>\n"
    msg += f"Showing {len(paginated['items'])} of {paginated['total_items']} projects\n\n"
    
    buttons = []
    for project in paginated['items']:
        # Get progress using sync_to_async to avoid async context issues
        from asgiref.sync import sync_to_async
        progress = await sync_to_async(project.get_progress_percentage)()
        status_emoji = MessageFormatter.get_status_emoji(project.status) if hasattr(project, 'status') else ''

        button_text = f"{status_emoji} {project.name} ({progress}%)"
        buttons.append(InlineKeyboardButton(button_text, callback_data=f"project:{project.id}"))
    
    # Add pagination buttons
    footer_buttons = []
    if paginated['total_pages'] > 1:
        footer_buttons.append(
            KeyboardBuilder.pagination_buttons(
                paginated['current_page'],
                paginated['total_pages'],
                "list_projects"
            )
        )
    
    # Add create button
    footer_buttons.append([InlineKeyboardButton("➕ Create Project", callback_data="create_project")])
    footer_buttons.append([KeyboardBuilder.back_button("menu")])
    
    keyboard = KeyboardBuilder.build_menu(buttons, n_cols=1, footer_buttons=footer_buttons)
    
    if update.message:
        await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    else:
        await update.callback_query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


async def project_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show project details."""
    query = update.callback_query
    await query.answer()
    
    project_id = int(query.data.split(':')[1])
    
    project_manager = ModelManager('core_tasks', 'Project')
    project = await project_manager.get(id=project_id)
    
    if not project:
        await query.edit_message_text("Project not found.")
        return
    
    msg = MessageFormatter.format_project(project)
    msg += f"\n\n{MessageFormatter.EMOJI['chart']} <b>Statistics:</b>\n"
    
    # Get task statistics
    task_manager = ModelManager('core_tasks', 'Task')
    all_tasks = await task_manager.filter(project_id=project_id)
    
    total_tasks = len(all_tasks)
    done_tasks = len([t for t in all_tasks if t.status == 'DONE'])
    in_progress = len([t for t in all_tasks if t.status == 'IN_PROGRESS'])
    todo_tasks = len([t for t in all_tasks if t.status == 'TODO'])
    
    msg += f"Total Tasks: {total_tasks}\n"
    msg += f"{MessageFormatter.EMOJI['done']} Done: {done_tasks}\n"
    msg += f"{MessageFormatter.EMOJI['in_progress']} In Progress: {in_progress}\n"
    msg += f"{MessageFormatter.EMOJI['todo']} To Do: {todo_tasks}\n"
    
    buttons = [
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['task']} View Tasks", callback_data=f"project_tasks:{project_id}")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['meeting']} Meetings", callback_data=f"project_meetings:{project_id}")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['report']} Reports", callback_data=f"project_reports:{project_id}")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['resource']} Resources", callback_data=f"project_resources:{project_id}")],
        [InlineKeyboardButton("➕ Add Task", callback_data=f"create_task:{project_id}")],
        [KeyboardBuilder.back_button("list_projects")],
    ]
    
    keyboard = KeyboardBuilder.build_menu([], n_cols=2, footer_buttons=buttons)
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)


# Conversation states for project creation
PROJECT_NAME, PROJECT_DESC, PROJECT_PRIORITY = range(3)


async def create_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start project creation conversation."""
    if update.callback_query:
        await update.callback_query.answer()
        msg = f"{MessageFormatter.EMOJI['project']} <b>Create New Project</b>\n\nPlease enter the project name:"
        await update.callback_query.edit_message_text(msg, parse_mode='HTML')
    else:
        msg = f"{MessageFormatter.EMOJI['project']} <b>Create New Project</b>\n\nPlease enter the project name:"
        await update.message.reply_text(msg, parse_mode='HTML')
    
    return PROJECT_NAME


async def project_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive project name."""
    context.user_data['project_name'] = update.message.text
    
    msg = f"{MessageFormatter.EMOJI['info']} Great! Now enter a description for the project (or /skip):"
    await update.message.reply_text(msg, parse_mode='HTML')
    
    return PROJECT_DESC


async def project_desc_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive project description."""
    if update.message.text != '/skip':
        context.user_data['project_desc'] = update.message.text
    else:
        context.user_data['project_desc'] = ''
    
    buttons = [
        [InlineKeyboardButton("🟢 Low", callback_data="priority:LOW")],
        [InlineKeyboardButton("🟡 Medium", callback_data="priority:MEDIUM")],
        [InlineKeyboardButton("🔴 High", callback_data="priority:HIGH")],
        [InlineKeyboardButton("🚨 Critical", callback_data="priority:CRITICAL")],
    ]
    keyboard = KeyboardBuilder.build_menu([], n_cols=2, footer_buttons=buttons)
    
    msg = f"{MessageFormatter.EMOJI['info']} Select project priority:"
    await update.message.reply_text(msg, parse_mode='HTML', reply_markup=keyboard)
    
    return PROJECT_PRIORITY


async def project_priority_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive project priority and create project."""
    query = update.callback_query
    await query.answer()
    
    priority = query.data.split(':')[1]
    user = await get_or_create_user(update, context)
    
    project_manager = ModelManager('core_tasks', 'Project')
    project = await project_manager.create(
        name=context.user_data['project_name'],
        description=context.user_data.get('project_desc', ''),
        priority=priority,
        owner_id=user.id,
        status='PLANNING'
    )
    
    msg = f"{MessageFormatter.EMOJI['success']} Project created successfully!\n\n"
    msg += MessageFormatter.format_project(project)
    
    buttons = [
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['task']} Add Task", callback_data=f"create_task:{project.id}")],
        [InlineKeyboardButton(f"{MessageFormatter.EMOJI['project']} View Project", callback_data=f"project:{project.id}")],
        [KeyboardBuilder.back_button("list_projects")],
    ]
    keyboard = KeyboardBuilder.build_menu([], n_cols=1, footer_buttons=buttons)
    
    await query.edit_message_text(msg, parse_mode='HTML', reply_markup=keyboard)
    
    # Clear user data
    context.user_data.clear()
    
    return ConversationHandler.END


async def cancel_project_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel project creation."""
    context.user_data.clear()
    await update.message.reply_text(
        f"{MessageFormatter.EMOJI['info']} Project creation cancelled.",
        parse_mode='HTML'
    )
    return ConversationHandler.END

