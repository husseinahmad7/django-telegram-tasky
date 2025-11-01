"""
Celery tasks for background processing.
Note: Celery is optional. If not installed, these tasks won't be available.
"""
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    # Celery not installed - create dummy decorator
    def shared_task(func):
        """Dummy decorator when Celery is not available."""
        return func
    CELERY_AVAILABLE = False

from django.utils import timezone
from datetime import timedelta
from django.conf import settings


@shared_task
def send_deadline_reminders():
    """Send reminders for upcoming deadlines."""
    from core_tasks.models import Task, Reminder
    from core_auth.models import TelegramUser
    
    # Get tasks with deadlines in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        deadline__lte=tomorrow,
        deadline__gte=timezone.now(),
        status__in=['TODO', 'IN_PROGRESS']
    )
    
    for task in upcoming_tasks:
        if task.assigned_to and task.assigned_to.notify_deadline_approaching:
            # Create reminder
            Reminder.objects.get_or_create(
                task=task,
                user=task.assigned_to,
                reminder_type='DEADLINE',
                defaults={
                    'reminder_time': task.deadline - timedelta(hours=2),
                    'message': f"Task '{task.title}' is due soon!",
                    'is_sent': False
                }
            )
    
    return f"Processed {upcoming_tasks.count()} upcoming tasks"


@shared_task
def send_overdue_alerts():
    """Send alerts for overdue tasks."""
    from core_tasks.models import Task, Alert
    from core_auth.models import TelegramUser
    
    # Get overdue tasks
    overdue_tasks = Task.objects.filter(
        deadline__lt=timezone.now(),
        status__in=['TODO', 'IN_PROGRESS']
    )
    
    for task in overdue_tasks:
        if task.assigned_to and task.assigned_to.notify_task_assigned:
            # Create alert
            Alert.objects.get_or_create(
                task=task,
                user=task.assigned_to,
                alert_type='OVERDUE',
                defaults={
                    'message': f"Task '{task.title}' is overdue!",
                    'is_read': False
                }
            )
    
    return f"Processed {overdue_tasks.count()} overdue tasks"


@shared_task
def send_meeting_reminders():
    """Send reminders for upcoming meetings."""
    from core_tasks.models import Meeting, Reminder
    
    # Get meetings in the next 2 hours
    soon = timezone.now() + timedelta(hours=2)
    upcoming_meetings = Meeting.objects.filter(
        scheduled_at__lte=soon,
        scheduled_at__gte=timezone.now()
    )

    for meeting in upcoming_meetings:
        # Get all participants (you'd need to add participants field to Meeting model)
        # For now, just notify the organizer
        if meeting.organizer and meeting.organizer.notify_meeting_scheduled:
            Reminder.objects.get_or_create(
                meeting=meeting,
                user=meeting.organizer,
                reminder_type='MEETING',
                defaults={
                    'reminder_time': meeting.scheduled_at - timedelta(minutes=30),
                    'message': f"Meeting '{meeting.title}' starts soon!",
                    'is_sent': False
                }
            )
    
    return f"Processed {upcoming_meetings.count()} upcoming meetings"


@shared_task
def process_pending_reminders():
    """Process and send pending reminders via Telegram."""
    from core_tasks.models import Reminder
    import requests
    
    # Get unsent reminders that are due
    pending_reminders = Reminder.objects.filter(
        is_sent=False,
        reminder_time__lte=timezone.now()
    )
    
    bot_token = settings.TELEGRAM_BOT_TOKEN
    sent_count = 0
    
    for reminder in pending_reminders:
        if reminder.user.telegram_id:
            try:
                # Send via Telegram API
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                data = {
                    'chat_id': reminder.user.telegram_id,
                    'text': f"🔔 Reminder:\n\n{reminder.message}",
                    'parse_mode': 'HTML'
                }
                
                response = requests.post(url, json=data)
                
                if response.status_code == 200:
                    reminder.is_sent = True
                    reminder.save()
                    sent_count += 1
            except Exception as e:
                print(f"Error sending reminder {reminder.id}: {e}")
    
    return f"Sent {sent_count} reminders"


@shared_task
def daily_report_reminder():
    """Remind users to submit daily reports."""
    from core_auth.models import TelegramUser
    from core_tasks.models import DailyReport
    import requests
    
    # Get users who haven't submitted today's report
    today = timezone.now().date()
    users_without_report = TelegramUser.objects.exclude(
        dailyreport__date=today
    ).filter(is_active=True, telegram_id__isnull=False)
    
    bot_token = settings.TELEGRAM_BOT_TOKEN
    sent_count = 0
    
    for user in users_without_report:
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': user.telegram_id,
                'text': "📊 Don't forget to submit your daily report!\n\nUse /dailyreport to submit.",
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=data)
            if response.status_code == 200:
                sent_count += 1
        except Exception as e:
            print(f"Error sending daily report reminder to {user.username}: {e}")
    
    return f"Sent {sent_count} daily report reminders"


@shared_task
def cleanup_old_notifications():
    """Clean up old read notifications and sent reminders."""
    from core_tasks.models import Alert, Reminder
    
    # Delete alerts older than 30 days
    old_date = timezone.now() - timedelta(days=30)
    deleted_alerts = Alert.objects.filter(
        created_at__lt=old_date,
        is_read=True
    ).delete()
    
    # Delete sent reminders older than 7 days
    old_reminder_date = timezone.now() - timedelta(days=7)
    deleted_reminders = Reminder.objects.filter(
        reminder_time__lt=old_reminder_date,
        is_sent=True
    ).delete()
    
    return f"Deleted {deleted_alerts[0]} alerts and {deleted_reminders[0]} reminders"

