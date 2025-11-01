# import os, django
# from telegram import Update

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tasky.settings')
# django.setup()
# # from Bot.telegram_bot import *
# # from django.conf import settings
# from Bot.bot import application, bot

# def main():
#     # from telegram_django_bot.tg_dj_bot import TG_DJ_Bot
#     # from telegram_django_bot.routing import RouterCallbackMessageCommandHandler
#     # # from asgiref.sync import sync_to_async

#     # bot = TG_DJ_Bot(settings.TELEGRAM_BOT_TOKEN)

#     # from telegram.ext import Updater, CommandHandler, ApplicationBuilder

#     # application = ApplicationBuilder().bot(bot).build()
#     # application.add_handler(RouterCallbackMessageCommandHandler())


#     # application.add_handler(CommandHandler("start", start))
#     # application.add_handler(CommandHandler("help", help_command))
#     # application.add_handler(CommandHandler("projects", list_projects))
#     # application.add_handler(CommandHandler("issues", list_issues))
#     # application.add_handler(CommandHandler("tasks", list_tasks))
#     # application.add_handler(CommandHandler("add_task", add_task))
#     # application.add_handler(CommandHandler("daily_report", daily_report))

#     application.run_polling(allowed_updates=Update.ALL_TYPES)
#     # application.run_webhook(webhook_url='https://82da-212-8-253-138.ngrok-free.app',allowed_updates=Update.ALL_TYPES)
#     globals()['application'] = application

# if __name__ == '__main__':
#     main()

