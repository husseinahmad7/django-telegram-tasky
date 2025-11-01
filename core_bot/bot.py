"""
Main bot application configuration.
Modular bot setup with dynamic handler registration.
"""
import logging
import sys
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, ContextTypes
from django.conf import settings

# Setup logging
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)

    # Try to notify the user
    try:
        error_message = (
            "❌ <b>Oops! Something went wrong.</b>\n\n"
            "Please try again or use /menu to return to the main menu.\n\n"
            "If the problem persists, contact support."
        )

        if update and update.effective_message:
            await update.effective_message.reply_text(error_message, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Error in error handler: {e}")


def create_bot_application():
    """Create and configure the bot application with dynamic handler registration."""

    logger.info("🤖 Creating bot application...")

    # Fix for PyInstaller: Configure httpx to work with frozen executables
    if getattr(sys, 'frozen', False):
        # Running as executable - use custom HTTP configuration
        from telegram.request import HTTPXRequest
        from httpx import Limits

        # Create request object with custom settings for PyInstaller
        request = HTTPXRequest(
            connection_pool_size=1,  # Minimal pool size
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
            http_version="1.1",  # Use HTTP/1.1 instead of HTTP/2
        )

        # Build application with custom request
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).request(request).build()
    else:
        # Running as script - use default configuration
        bot = Bot(settings.TELEGRAM_BOT_TOKEN)
        application = ApplicationBuilder().bot(bot).build()

    # Register handlers from all installed apps dynamically
    from core_bot.registry import registry
    registry.register_all_handlers(application)

    # Error handler (must be added last)
    application.add_error_handler(error_handler)

    logger.info("✅ Bot application created successfully")
    logger.info(f"📦 Registered apps: {', '.join(registry.get_app_names())}")

    return application


# Create the application instance
application = create_bot_application()

