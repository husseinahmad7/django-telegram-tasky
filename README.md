# 🚀 Tasky - Modern Telegram Project Management Bot

A feature-rich Telegram bot for company project management with task tracking, deadlines, meetings, approvals, and more.

## ✨ Features

### 📁 Project Management
- Create and manage multiple projects
- Track project progress and status
- Assign teams and roles
- Project-level statistics and reports

### 📝 Task Management
- Create, assign, and track tasks
- Set priorities (Low, Medium, High, Urgent)
- Deadline tracking with reminders
- Task dependencies
- Status workflow (To Do → In Progress → Review → Done)
- Task comments and attachments

### 👥 User & Role Management
- Custom user roles with permissions
- Team groups and assignments
- Role-based access control
- User project assignments

### 📊 Reports & Analytics
- Daily progress reports
- Weekly summaries
- Project progress tracking
- Task completion statistics

### 📅 Meeting Management
- Schedule meetings
- Meeting time voting
- Participant management
- Meeting reminders

### ✔️ Approval Workflow
- Task approval requests
- Project approvals
- Approval notifications

### 🔔 Notifications & Alerts
- Task assignment alerts
- Deadline reminders (daily/weekly) - *Automatic with Celery*
- Meeting notifications - *Automatic with Celery*
- Approval requests
- Customizable notification preferences
- Manual notifications (always available)

### 📚 Learning Resources
- Share documentation and resources
- Link resources to projects/tasks
- Categorize by type (Article, Video, Tutorial, etc.)

## 🛠️ Tech Stack

- **Python 3.14**
- **Django 5.2.7** - Web framework
- **python-telegram-bot** - Telegram Bot API
- **SQLite** - Database (easily switchable to PostgreSQL)
- **Starlette** - ASGI server
- **UV** - Fast Python package manager
- **Celery** - Optional background tasks (for automatic reminders)
- **Redis** - Optional (required only if using Celery)
- **Google Gemini AI** - Optional AI features

## 📦 Installation

### Prerequisites
- Python 3.14+
- UV package manager
- Telegram Bot Token (from @BotFather)
- ngrok (for local development)

### Setup

1. **Clone the repository**
```bash
cd d:\Python-projects\Tasky
```

2. **Install UV** (if not installed)
```bash
pip install uv
```

3. **Install dependencies**
```bash
uv pip install -e .
```

4. **Configure environment variables**

Edit `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GEMINI_API_KEY=your_gemini_key_here  # Optional
NGROK_AUTHTOKEN=your_ngrok_token_here
WEBHOOK_URL=  # Will be set dynamically
```

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Create default roles**
```bash
python manage.py shell
```
```python
from core_auth.models import Role

# Create default roles
Role.objects.create(
    name="Owner",
    role_type="OWNER",
    can_create_projects=True,
    can_edit_projects=True,
    can_delete_projects=True,
    can_assign_tasks=True,
    can_approve_tasks=True,
    can_manage_users=True,
    can_schedule_meetings=True
)

Role.objects.create(
    name="Manager",
    role_type="MANAGER",
    can_create_projects=True,
    can_edit_projects=True,
    can_assign_tasks=True,
    can_approve_tasks=True,
    can_schedule_meetings=True
)

Role.objects.create(
    name="Developer",
    role_type="DEVELOPER",
    can_create_tasks=True,
    can_edit_tasks=True
)
```

## 🚀 Running the Bot

### Quick Start (Recommended)

The easiest way to start the bot:

```bash
python start_bot.py
```

This will:
- ✅ Automatically start ngrok
- ✅ Set the webhook
- ✅ Start the server
- ✅ Handle everything for you!

### Development (Manual)

1. **Start ngrok**
```bash
ngrok http 8000
```

2. **Set webhook** (use the ngrok URL)
```bash
python manage.py set_webhook https://your-ngrok-url.ngrok-free.app
```

3. **Run the server**
```bash
uvicorn Tasky.asgi:app --host 0.0.0.0 --port 8000 --reload
```

### Optional: Enable Automatic Reminders (Celery)

**Note:** Celery is completely optional! The bot works perfectly without it.

If you want automatic deadline reminders and notifications:

1. **Install Celery and Redis**
```bash
pip install celery redis
```

2. **Start Redis**
```bash
# Windows (Docker)
docker run -d -p 6379:6379 redis

# Linux
sudo systemctl start redis

# macOS
brew services start redis
```

3. **Start Celery Worker** (new terminal)
```bash
celery -A Tasky worker -l info
```

4. **Start Celery Beat** (new terminal)
```bash
celery -A Tasky beat -l info
```

See `CELERY_OPTIONAL.md` for complete guide.

### Production

1. **Set webhook to your domain**
```bash
python manage.py set_webhook https://yourdomain.com
```

2. **Run with Gunicorn**
```bash
gunicorn Tasky.asgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📱 Bot Commands

### Basic Commands
- `/start` - Welcome message and main menu
- `/help` - Show all available commands
- `/menu` - Display main menu

### Project Commands
- `/projects` - List all projects
- `/myprojects` - Your projects
- `/createproject` - Create new project

### Task Commands
- `/tasks` - List all tasks
- `/mytasks` - Your assigned tasks
- `/createtask` - Create new task

### Report Commands
- `/dailyreport` - Submit daily report
- `/weeklyreport` - View weekly summary

### Meeting Commands
- `/meetings` - List upcoming meetings
- `/schedulemeeting` - Schedule new meeting

### Approval Commands
- `/approvals` - Pending approvals
- `/approve [id]` - Approve request
- `/reject [id]` - Reject request

## 🏗️ Project Structure

```
Tasky/
├── core_auth/          # Reusable authentication & roles
│   ├── models.py       # TelegramUser, Role, TeamGroup
│   └── admin.py
├── core_tasks/         # Reusable task management
│   ├── models.py       # Project, Task, Meeting, etc.
│   └── admin.py
├── core_bot/           # Reusable bot logic
│   ├── bot.py          # Main bot configuration
│   ├── utils.py        # Utilities (ModelManager, KeyboardBuilder)
│   ├── handlers/       # Command handlers
│   │   ├── basic.py
│   │   ├── projects.py
│   │   ├── tasks.py
│   │   ├── reports.py
│   │   ├── meetings.py
│   │   └── approvals.py
│   └── management/     # Management commands
├── Bot/                # Legacy bot (deprecated)
├── ProjectMng/         # Legacy models (deprecated)
├── Tasky/              # Django project
│   ├── settings.py
│   ├── asgi.py         # ASGI + Telegram webhook
│   └── urls.py
├── pyproject.toml      # UV dependencies
├── .env                # Environment variables
└── README.md
```

## 🔧 Configuration

### Database
By default, SQLite is used. To switch to PostgreSQL:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tasky',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Celery (Optional - for background tasks)
```bash
# Install Redis
# Start Celery worker
celery -A Tasky worker -l info
```

## 📦 Building Executable

To create a standalone executable:

```bash
uv pip install pyinstaller
pyinstaller --name Tasky --onefile manage.py
```

## 🎨 Customization

### Adding New Commands

1. Create handler in `core_bot/handlers/`
2. Register in `core_bot/bot.py`
3. Add to `__init__.py` exports

### Adding New Models

1. Add model to appropriate core app
2. Run migrations
3. Register in admin.py

## 🤝 Contributing

This is a modular, reusable architecture. Core apps (`core_auth`, `core_tasks`, `core_bot`) can be extracted and used in other Django projects.

## 📄 License

MIT License

## 🆘 Support

For issues and questions, please check the `/help` command in the bot or refer to the Django admin panel.

## 🎯 Roadmap

- [x] Basic project and task management
- [x] User roles and permissions
- [x] Modern inline keyboard UI
- [ ] Meeting voting system
- [ ] AI-powered task suggestions (Gemini)
- [ ] Advanced reporting and analytics
- [ ] File attachment handling
- [ ] Calendar integration
- [ ] Mobile app companion

---

Made with ❤️ for modern project management

