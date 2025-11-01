"""
Reusable bot utilities for Telegram integration.
"""
from typing import List, Optional, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist


class ModelManager:
    """Async model manager for database operations."""
    
    def __init__(self, app_label: str, model_name: str):
        self.model = apps.get_model(app_label, model_name)
    
    @sync_to_async
    def create(self, **kwargs):
        """Create a new instance."""
        return self.model.objects.create(**kwargs)
    
    @sync_to_async
    def get(self, **kwargs):
        """Get a single instance."""
        try:
            return self.model.objects.get(**kwargs)
        except ObjectDoesNotExist:
            return None
    
    @sync_to_async
    def filter(self, **kwargs):
        """Filter instances."""
        return list(self.model.objects.filter(**kwargs))
    
    @sync_to_async
    def all(self):
        """Get all instances."""
        return list(self.model.objects.all())
    
    @sync_to_async
    def update(self, pk, **kwargs):
        """Update an instance."""
        try:
            instance = self.model.objects.get(pk=pk)
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.save()
            return instance
        except ObjectDoesNotExist:
            return None
    
    @sync_to_async
    def delete(self, pk):
        """Delete an instance."""
        try:
            instance = self.model.objects.get(pk=pk)
            instance.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    @sync_to_async
    def count(self, **kwargs):
        """Count instances."""
        if kwargs:
            return self.model.objects.filter(**kwargs).count()
        return self.model.objects.count()


class KeyboardBuilder:
    """Helper class for building inline keyboards."""
    
    @staticmethod
    def build_menu(
        buttons: List[InlineKeyboardButton],
        n_cols: int = 2,
        header_buttons: Optional[List[InlineKeyboardButton]] = None,
        footer_buttons: Optional[List] = None
    ) -> InlineKeyboardMarkup:
        """
        Build a menu with buttons arranged in columns.

        Args:
            buttons: List of buttons to arrange in grid
            n_cols: Number of columns
            header_buttons: Single row of buttons to add at top (list of buttons)
            footer_buttons: Rows to add at bottom (list of lists OR list of buttons)
        """
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]

        if header_buttons:
            menu.insert(0, header_buttons)

        if footer_buttons:
            # Handle both list of buttons and list of lists
            if len(footer_buttons) > 0 and isinstance(footer_buttons[0], list):
                # Already a list of lists
                menu.extend(footer_buttons)
            elif len(footer_buttons) > 0:
                # Single list of buttons
                menu.append(footer_buttons)

        return InlineKeyboardMarkup(menu)
    
    @staticmethod
    def pagination_buttons(
        current_page: int,
        total_pages: int,
        callback_prefix: str
    ) -> List[InlineKeyboardButton]:
        """Create pagination buttons."""
        buttons = []
        
        if current_page > 0:
            buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}:{current_page - 1}")
            )
        
        buttons.append(
            InlineKeyboardButton(f"📄 {current_page + 1}/{total_pages}", callback_data="noop")
        )
        
        if current_page < total_pages - 1:
            buttons.append(
                InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}:{current_page + 1}")
            )
        
        return buttons
    
    @staticmethod
    def back_button(callback_data: str = "back") -> InlineKeyboardButton:
        """Create a back button."""
        return InlineKeyboardButton("🔙 Back", callback_data=callback_data)
    
    @staticmethod
    def cancel_button(callback_data: str = "cancel") -> InlineKeyboardButton:
        """Create a cancel button."""
        return InlineKeyboardButton("❌ Cancel", callback_data=callback_data)


class MessageFormatter:
    """Helper class for formatting messages."""
    
    # Emoji constants
    EMOJI = {
        'project': '📁',
        'task': '📝',
        'done': '✅',
        'todo': '⏳',
        'in_progress': '🔄',
        'blocked': '🚫',
        'review': '👀',
        'high_priority': '🔴',
        'medium_priority': '🟡',
        'low_priority': '🟢',
        'urgent': '🚨',
        'deadline': '⏰',
        'meeting': '📅',
        'user': '👤',
        'team': '👥',
        'alert': '🔔',
        'approval': '✔️',
        'report': '📊',
        'resource': '📚',
        'calendar': '📆',
        'chart': '📈',
        'warning': '⚠️',
        'info': 'ℹ️',
        'success': '✨',
        'settings': '⚙️',
        'error': '❌',
    }
    
    @staticmethod
    def get_status_emoji(status: str) -> str:
        """Get emoji for status."""
        status_map = {
            'TODO': MessageFormatter.EMOJI['todo'],
            'IN_PROGRESS': MessageFormatter.EMOJI['in_progress'],
            'REVIEW': MessageFormatter.EMOJI['review'],
            'BLOCKED': MessageFormatter.EMOJI['blocked'],
            'DONE': MessageFormatter.EMOJI['done'],
            'CANCELLED': MessageFormatter.EMOJI['error'],
        }
        return status_map.get(status, '')
    
    @staticmethod
    def get_priority_emoji(priority: str) -> str:
        """Get emoji for priority."""
        priority_map = {
            'LOW': MessageFormatter.EMOJI['low_priority'],
            'MEDIUM': MessageFormatter.EMOJI['medium_priority'],
            'HIGH': MessageFormatter.EMOJI['high_priority'],
            'URGENT': MessageFormatter.EMOJI['urgent'],
            'CRITICAL': MessageFormatter.EMOJI['urgent'],
        }
        return priority_map.get(priority, '')
    
    @staticmethod
    def format_task(task: Any) -> str:
        """Format task information."""
        status_emoji = MessageFormatter.get_status_emoji(task.status)
        priority_emoji = MessageFormatter.get_priority_emoji(task.priority)
        
        msg = f"{status_emoji} <b>{task.title}</b>\n"
        msg += f"{priority_emoji} Priority: {task.get_priority_display()}\n"
        
        if task.assigned_to:
            msg += f"{MessageFormatter.EMOJI['user']} Assigned to: {task.assigned_to.get_full_name()}\n"
        
        if task.deadline:
            days = task.days_until_deadline
            if days is not None:
                if days < 0:
                    msg += f"{MessageFormatter.EMOJI['warning']} Overdue by {abs(days)} days\n"
                elif days == 0:
                    msg += f"{MessageFormatter.EMOJI['deadline']} Due today!\n"
                else:
                    msg += f"{MessageFormatter.EMOJI['deadline']} Due in {days} days\n"
        
        if task.description:
            msg += f"\n{task.description[:200]}"
            if len(task.description) > 200:
                msg += "..."
        
        return msg
    
    @staticmethod
    def format_project(project: Any, include_progress: bool = False) -> str:
        """
        Format project information.

        Args:
            project: Project instance
            include_progress: If True, includes progress (requires sync context)
        """
        msg = f"{MessageFormatter.EMOJI['project']} <b>{project.name}</b>\n"
        msg += f"Status: {project.get_status_display()}\n"

        # Only include progress if explicitly requested and safe to do so
        # In async contexts, calculate progress separately using sync_to_async
        if include_progress and hasattr(project, '_progress'):
            msg += f"Progress: {project._progress}%\n"

        if project.description:
            msg += f"\n{project.description[:150]}"
            if len(project.description) > 150:
                msg += "..."

        return msg
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text


async def get_or_create_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get or create user from Telegram update."""
    from core_auth.models import TelegramUser
    
    telegram_user = update.effective_user
    if not telegram_user:
        return None
    
    user_manager = ModelManager('core_auth', 'TelegramUser')
    user = await user_manager.get(telegram_id=telegram_user.id)
    
    if not user:
        # Create new user
        username = telegram_user.username or f"user_{telegram_user.id}"
        user = await user_manager.create(
            telegram_id=telegram_user.id,
            username=username,
            telegram_username=telegram_user.username or '',
            telegram_first_name=telegram_user.first_name or '',
            telegram_last_name=telegram_user.last_name or '',
            language_code=telegram_user.language_code or 'en',
        )
    
    return user


def paginate_items(items: List[Any], page: int = 0, per_page: int = 10):
    """Paginate a list of items."""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    start_idx = page * per_page
    end_idx = start_idx + per_page
    
    return {
        'items': items[start_idx:end_idx],
        'current_page': page,
        'total_pages': total_pages,
        'total_items': total_items,
        'has_next': page < total_pages - 1,
        'has_prev': page > 0,
    }

