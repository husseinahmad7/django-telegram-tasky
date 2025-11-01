# 🚀 Quick Start Guide

Get Tasky bot running in 5 minutes!

## Prerequisites

- Python 3.14+ (or 3.12+ will work)
- Telegram Bot Token from [@BotFather](https://t.me/botfather)
- ngrok installed (for local testing)

## Step-by-Step Setup

### 1. Install Dependencies

**Option A: Using UV (Recommended)**
```bash
pip install uv
uv pip install -r requirements.txt
```

**Option B: Using pip**
```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` file should have:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_key_here  # Optional
NGROK_AUTHTOKEN=your_ngrok_token_here
```

### 3. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Create Initial Data

```bash
python manage.py shell
```

Then run:
```python
from core_auth.models import Role, TelegramUser

# Create admin role
Role.objects.create(
    name="Admin",
    role_type="ADMIN",
    can_create_projects=True,
    can_edit_projects=True,
    can_delete_projects=True,
    can_create_tasks=True,
    can_edit_tasks=True,
    can_delete_tasks=True,
    can_assign_tasks=True,
    can_approve_tasks=True,
    can_view_reports=True,
    can_manage_users=True,
    can_schedule_meetings=True
)

# Create developer role
Role.objects.create(
    name="Developer",
    role_type="DEVELOPER",
    can_create_tasks=True,
    can_edit_tasks=True,
    can_view_reports=True
)

exit()
```

### 5. Start the Bot

**Automatic (Recommended)**
```bash
python start_bot.py
```

This will:
- Start ngrok automatically
- Set the webhook
- Start the server

**Manual**

Terminal 1 - Start ngrok:
```bash
ngrok http 8000
```

Terminal 2 - Set webhook (use ngrok URL):
```bash
python manage.py set_webhook https://your-ngrok-url.ngrok-free.app
```

Terminal 3 - Start server:
```bash
uvicorn Tasky.asgi:app --host 0.0.0.0 --port 8000 --reload
```

### 6. Test the Bot

1. Open Telegram
2. Find your bot
3. Send `/start`
4. You should see the welcome message!

## 🎯 First Steps

1. **Create a Project**
   - Send `/createproject`
   - Follow the prompts

2. **Create a Task**
   - Send `/createtask`
   - Or use inline buttons from project view

3. **View Your Tasks**
   - Send `/mytasks`
   - Click on tasks to see details

4. **Update Task Status**
   - Click on a task
   - Use status buttons to update

## 🔧 Troubleshooting

### Bot not responding?

1. Check webhook status:
```bash
python manage.py shell
```
```python
from core_bot.bot import application
import asyncio

async def check():
    info = await application.bot.get_webhook_info()
    print(f"URL: {info.url}")
    print(f"Pending: {info.pending_update_count}")
    print(f"Last Error: {info.last_error_message}")

asyncio.run(check())
```

2. Check server logs for errors

3. Verify `.env` has correct `TELEGRAM_BOT_TOKEN`

### Database errors?

```bash
# Reset database (WARNING: deletes all data)
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Import errors?

Make sure you're in the project directory and virtual environment is activated.

## 📱 Admin Panel

Access Django admin at: `http://localhost:8000/django/admin/`

Here you can:
- Manage users and roles
- Create projects and tasks manually
- View all data
- Configure permissions

## 🎨 Customization

### Change Bot Messages

Edit files in `core_bot/handlers/`

### Add New Commands

1. Create handler function
2. Add to `core_bot/bot.py`
3. Restart server

### Modify Models

1. Edit models in `core_auth/models.py` or `core_tasks/models.py`
2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

## 📚 Next Steps

- Read full [README.md](README.md)
- Explore bot commands with `/help`
- Check out the admin panel
- Customize for your team's needs

## 🆘 Need Help?

- Check bot `/help` command
- Review Django admin panel
- Check server logs
- Verify webhook is set correctly

---

Happy task managing! 🎉

