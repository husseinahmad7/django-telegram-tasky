# import asyncio
# import uvicorn
# import asyncio
# from telegram import Update
# import os, django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tasky.settings')
# django.setup()
# from Bot.bot import application

# async def main():
#     await application.bot.set_webhook('https://1647-185-107-56-124.ngrok-free.app/telegram',allowed_updates=Update.ALL_TYPES)

#     config = uvicorn.Config("Tasky.asgi:app", port=8000, log_level="info")
#     server = uvicorn.Server(config)
#     async with application:
#         await application.start()
#         await server.serve()
#         await application.stop()


# if __name__ == "__main__":
#     asyncio.run(main())