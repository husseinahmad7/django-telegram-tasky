#!/usr/bin/env python
"""
Startup script for Tasky bot.
Handles ngrok setup and webhook configuration automatically.
"""
import os
import sys
import asyncio
import subprocess
import time
import requests
from pathlib import Path

# Disable output buffering for immediate console output
os.environ['PYTHONUNBUFFERED'] = '1'

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        # Try to set UTF-8 encoding for console output
        import codecs
        import io

        # Create unbuffered UTF-8 writers
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='strict',
            line_buffering=True,  # Line buffering for immediate output
            write_through=True    # Write through immediately
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding='utf-8',
            errors='strict',
            line_buffering=True,
            write_through=True
        )
    except Exception:
        # If that fails, silently continue (emojis will be replaced)
        pass

# Determine if running as executable or script
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    BASE_DIR = Path(sys.executable).resolve().parent
    IS_EXECUTABLE = True
else:
    # Running as script
    BASE_DIR = Path(__file__).resolve().parent
    IS_EXECUTABLE = False

sys.path.insert(0, str(BASE_DIR))

# Load .env from executable directory
from dotenv import load_dotenv
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from: {env_path}")
else:
    print(f"⚠️  No .env file found at: {env_path}")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tasky.settings')
import django
django.setup()

from django.conf import settings
from telegram import Update


def start_ngrok():
    """Start ngrok and return the public URL."""
    print("🚀 Starting ngrok...")
    sys.stdout.flush()  # Force flush

    # Start ngrok in background
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', '8000'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for ngrok to start
    time.sleep(3)

    # Get ngrok URL from API
    try:
        response = requests.get('http://localhost:4040/api/tunnels')
        tunnels = response.json()['tunnels']

        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                url = tunnel['public_url']
                print(f"✅ ngrok URL: {url}")
                sys.stdout.flush()  # Force flush
                return url, ngrok_process
    except Exception as e:
        print(f"❌ Failed to get ngrok URL: {e}")
        print("Make sure ngrok is installed and running")
        sys.stdout.flush()  # Force flush
        return None, ngrok_process

    return None, ngrok_process


async def set_webhook(webhook_url):
    """Set the Telegram webhook."""
    from core_bot.bot import application
    
    full_url = f"{webhook_url}/telegram/"
    print(f"🔗 Setting webhook to: {full_url}")
    
    try:
        await application.bot.set_webhook(full_url, allowed_updates=Update.ALL_TYPES)
        webhook_info = await application.bot.get_webhook_info()
        print(f"✅ Webhook set successfully!")
        print(f"   URL: {webhook_info.url}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        return True
    except Exception as e:
        print(f"❌ Failed to set webhook: {e}")
        return False


async def validate_webhook(webhook_url):
    """Validate webhook URL and bot token."""
    from core_bot.bot import application

    full_url = f"{webhook_url}/telegram/"
    print(f"🔍 Validating bot and setting webhook to: {full_url}")
    sys.stdout.flush()  # Force flush

    try:
        # Initialize bot to validate token
        await application.initialize()

        # Set webhook
        await application.bot.set_webhook(full_url, allowed_updates=Update.ALL_TYPES)
        webhook_info = await application.bot.get_webhook_info()

        print(f"✅ Webhook set successfully!")
        print(f"   URL: {webhook_info.url}")
        print(f"   Pending updates: {webhook_info.pending_update_count}")
        sys.stdout.flush()  # Force flush

        # IMPORTANT: Shutdown to clean up this temporary initialization
        await application.shutdown()

        return True
    except Exception as e:
        print(f"❌ Failed to validate: {e}")
        sys.stdout.flush()  # Force flush
        try:
            await application.shutdown()
        except:
            pass
        return False


def run_async_validation(webhook_url):
    """Run async validation in a new event loop that we control."""
    # Create a new event loop for validation
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(validate_webhook(webhook_url))
        return result
    finally:
        # Don't close the loop - let it be reused
        # Just clear it as the current loop
        asyncio.set_event_loop(None)


def start_server():
    """Start the uvicorn server."""
    print("🌐 Starting server on http://0.0.0.0:8000")
    print("📱 Bot is ready! Send /start to your bot on Telegram")
    print("\nPress Ctrl+C to stop\n")
    sys.stdout.flush()  # Force flush before starting server

    if IS_EXECUTABLE:
        # Running as executable - use uvicorn programmatically
        import uvicorn
        from Tasky.asgi import app

        uvicorn.run(
            app,
            host='0.0.0.0',
            port=8000,
            log_level='info'
        )
    else:
        # Running as script - use subprocess for hot reload
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'Tasky.asgi:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])


def main():
    """Main startup function."""
    print("=" * 60)
    print("🤖 Tasky Bot Startup")
    print("=" * 60)
    sys.stdout.flush()  # Force flush

    # Check if webhook URL is provided
    webhook_url = os.getenv('WEBHOOK_URL')
    ngrok_process = None

    if not webhook_url:
        print("\n⚠️  No WEBHOOK_URL found in .env")
        print("Starting ngrok automatically...\n")
        sys.stdout.flush()  # Force flush

        webhook_url, ngrok_process = start_ngrok()

        if not webhook_url:
            print("\n❌ Failed to start ngrok. Please:")
            print("   1. Install ngrok: https://ngrok.com/download")
            print("   2. Or set WEBHOOK_URL in .env manually")
            sys.stdout.flush()  # Force flush
            sys.exit(1)

    # Set webhook
    success = run_async_validation(webhook_url)

    # success = asyncio.run(set_webhook(webhook_url))

    if not success:
        print("\n❌ Failed to set webhook. Check your bot token.")
        sys.stdout.flush()  # Force flush
        if ngrok_process:
            ngrok_process.terminate()
        sys.exit(1)

    # Store webhook URL for the server to use
    os.environ['WEBHOOK_URL'] = webhook_url

    print()
    print("=" * 60)
    sys.stdout.flush()  # Force flush

    try:
        # Start server
        start_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        if ngrok_process:
            ngrok_process.terminate()
        print("✅ Goodbye!")
        sys.stdout.flush()  # Force flush


if __name__ == '__main__':
    main()

