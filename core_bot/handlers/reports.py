"""
Report handlers - daily and weekly reports.
"""
from telegram import Update
from telegram.ext import ContextTypes
from core_bot.utils import get_or_create_user, ModelManager, MessageFormatter
from datetime import date


async def daily_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Submit daily report."""
    user = await get_or_create_user(update, context)
    
    msg = f"{MessageFormatter.EMOJI['report']} <b>Daily Report</b>\n\n"
    msg += "Please send your daily report in the following format:\n\n"
    msg += "<b>Completed:</b> Task 1, Task 2\n"
    msg += "<b>In Progress:</b> Task 3\n"
    msg += "<b>Blockers:</b> None\n"
    msg += "<b>Tomorrow:</b> Task 4, Task 5\n"
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def weekly_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View weekly summary."""
    user = await get_or_create_user(update, context)
    
    msg = f"{MessageFormatter.EMOJI['chart']} <b>Weekly Summary</b>\n\n"
    msg += "Feature coming soon!\n"
    msg += "This will show your weekly progress, completed tasks, and statistics."
    
    await update.message.reply_text(msg, parse_mode='HTML')

