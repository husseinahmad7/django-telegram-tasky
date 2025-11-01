"""
Management command to set Telegram webhook.
"""
import asyncio
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update


class Command(BaseCommand):
    help = "Set the Telegram bot webhook URL"

    def add_arguments(self, parser):
        parser.add_argument(
            'webhook_url',
            type=str,
            help='The webhook URL (e.g., https://your-domain.ngrok-free.app)'
        )

    def handle(self, *args, **options):
        webhook_url = options['webhook_url']
        
        async def set_webhook():
            from core_bot.bot import application
            
            full_url = f"{webhook_url}/telegram/"
            await application.bot.set_webhook(full_url, allowed_updates=Update.ALL_TYPES)
            
            webhook_info = await application.bot.get_webhook_info()
            self.stdout.write(
                self.style.SUCCESS(f'Webhook set successfully to: {webhook_info.url}')
            )
            self.stdout.write(f'Pending updates: {webhook_info.pending_update_count}')
        
        asyncio.run(set_webhook())

