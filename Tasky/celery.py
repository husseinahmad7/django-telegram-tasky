"""
Celery configuration for Tasky project.
Note: This file is only used if Celery is installed.
"""
import os

try:
    from celery import Celery
    from celery.schedules import crontab
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create dummy objects
    class Celery:
        def __init__(self, *args, **kwargs):
            pass
        def config_from_object(self, *args, **kwargs):
            pass
        def autodiscover_tasks(self, *args, **kwargs):
            pass
        def task(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

    def crontab(*args, **kwargs):
        return None

if not CELERY_AVAILABLE:
    app = None
else:

    # Set the default Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tasky.settings')

    app = Celery('Tasky')

    # Load configuration from Django settings with CELERY namespace
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Auto-discover tasks in all installed apps
    app.autodiscover_tasks()

    # Periodic task schedule
    app.conf.beat_schedule = {
        'send-deadline-reminders-every-hour': {
            'task': 'core_tasks.tasks.send_deadline_reminders',
            'schedule': crontab(minute=0),  # Every hour
        },
        'send-overdue-alerts-every-6-hours': {
            'task': 'core_tasks.tasks.send_overdue_alerts',
            'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        },
        'send-meeting-reminders-every-30-minutes': {
            'task': 'core_tasks.tasks.send_meeting_reminders',
            'schedule': crontab(minute='*/30'),  # Every 30 minutes
        },
        'process-pending-reminders-every-5-minutes': {
            'task': 'core_tasks.tasks.process_pending_reminders',
            'schedule': crontab(minute='*/5'),  # Every 5 minutes
        },
        'daily-report-reminder-at-5pm': {
            'task': 'core_tasks.tasks.daily_report_reminder',
            'schedule': crontab(hour=17, minute=0),  # 5 PM daily
        },
        'cleanup-old-notifications-daily': {
            'task': 'core_tasks.tasks.cleanup_old_notifications',
            'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        },
    }

    # Timezone
    app.conf.timezone = 'UTC'


    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        """Debug task for testing Celery."""
        print(f'Request: {self.request!r}')

