"""
ASGI config for Tasky project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tasky.settings')

django_application = get_asgi_application()

# Import the new bot application
from core_bot.bot import application
from telegram import Update
from contextlib import asynccontextmanager
from starlette.responses import Response

# Determine base directory (works for both script and executable)
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Running as script
    BASE_DIR = Path(__file__).resolve().parent.parent


async def telegram_webhook(request):
    """Handle incoming Telegram webhook requests."""
    if request.method == "POST":
        update = Update.de_json(data=await request.json(), bot=application.bot)
        await application.process_update(update)
        return Response()
    else:
        return Response(status=400)

# Starlette serving
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from django.conf import settings

@asynccontextmanager
async def ptb_lifespan(app):
    """Manage bot lifecycle - set webhook and start/stop application."""
    # Initialize the application first (before setting webhook)
    await application.initialize()
    await application.start()
    
    # Now set webhook
    webhook_url = settings.WEBHOOK_URL or os.getenv('WEBHOOK_URL', '')
    if webhook_url:
        try:
            await application.bot.set_webhook(
                f'{webhook_url}/telegram/',
                allowed_updates=Update.ALL_TYPES
            )
        except Exception as e:
            print(f"Warning: Failed to set webhook during startup: {e}")
    
    yield
    
    # Cleanup
    await application.stop()
    await application.shutdown()

# @asynccontextmanager
# async def ptb_lifespan(app):
#     """Manage bot lifecycle - set webhook and start/stop application."""
#     webhook_url = settings.WEBHOOK_URL or os.getenv('WEBHOOK_URL', '')

#     if webhook_url:
#         await application.bot.set_webhook(
#             f'{webhook_url}/telegram/',
#             allowed_updates=Update.ALL_TYPES
#         )

#     async with application:
#         await application.start()
#         yield
#         await application.stop()


# Build routes list
routes = [
    Route("/telegram/", telegram_webhook, methods=['POST']),
]

# Add static files mount if directory exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    routes.append(Mount("/static/", StaticFiles(directory=str(static_dir)), name="static"))

# Add Django mount
routes.append(Mount("/django/", django_application))

app = Starlette(
    routes=routes,
    lifespan=ptb_lifespan,
)
