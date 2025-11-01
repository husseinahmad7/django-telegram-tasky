"""
Core task management models.
Reusable across projects.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class Project(models.Model):
    """Project model with enhanced features."""

    STATUS_CHOICES = [
        ('PLANNING', _('Planning')),
        ('ACTIVE', _('Active')),
        ('ON_HOLD', _('On Hold')),
        ('COMPLETED', _('Completed')),
        ('ARCHIVED', _('Archived')),
    ]

    PRIORITY_CHOICES = [
        ('LOW', _('Low')),
        ('MEDIUM', _('Medium')),
        ('HIGH', _('High')),
        ('CRITICAL', _('Critical')),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    owner = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    # Team members can be managed through Django Groups
    # Use owner.groups or create a ManyToMany to TelegramUser if needed
    members = models.ManyToManyField(
        'core_auth.TelegramUser',
        related_name='member_projects',
        blank=True,
        help_text=_('Project team members')
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    telegram_chat_id = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_progress_percentage(self):
        """
        Calculate project completion percentage.
        Note: This is a regular method, not a property, to avoid async issues.
        Call with sync_to_async when in async context.
        """
        total_tasks = self.tasks.count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.tasks.filter(status='DONE').count()
        return int((completed_tasks / total_tasks) * 100)


class Task(models.Model):
    """Enhanced task model with deadlines and tracking."""

    STATUS_CHOICES = [
        ('TODO', _('To Do')),
        ('IN_PROGRESS', _('In Progress')),
        ('REVIEW', _('In Review')),
        ('BLOCKED', _('Blocked')),
        ('DONE', _('Done')),
        ('CANCELLED', _('Cancelled')),
    ]

    PRIORITY_CHOICES = [
        ('LOW', _('Low')),
        ('MEDIUM', _('Medium')),
        ('HIGH', _('High')),
        ('URGENT', _('Urgent')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TODO')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    assigned_to = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    created_by = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )

    # Deadlines
    deadline = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    # Dependencies
    depends_on = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='blocking_tasks'
    )

    # Tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        ordering = ['-priority', '-created_at']

    def __str__(self):
        return f"{self.project.name} - {self.title}"

    @property
    def is_overdue(self):
        """Check if task is overdue."""
        if self.deadline and self.status not in ['DONE', 'CANCELLED']:
            return timezone.now() > self.deadline
        return False

    @property
    def days_until_deadline(self):
        """Calculate days until deadline."""
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None


class TaskComment(models.Model):
    """Comments on tasks."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='task_comments'
    )
    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Task Comment')
        verbose_name_plural = _('Task Comments')
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.task.title} by {self.user}"


class TaskAttachment(models.Model):
    """File attachments for tasks."""

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    uploaded_by = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )
    file = models.FileField(upload_to='task_attachments/%Y/%m/')
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    telegram_file_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Task Attachment')
        verbose_name_plural = _('Task Attachments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.file_name} - {self.task.title}"


class DailyReport(models.Model):
    """Daily progress reports."""

    user = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='daily_reports'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='daily_reports',
        null=True,
        blank=True
    )
    date = models.DateField(default=timezone.now)

    tasks_completed = models.ManyToManyField(
        Task,
        related_name='completed_in_reports',
        blank=True
    )
    tasks_in_progress = models.ManyToManyField(
        Task,
        related_name='in_progress_in_reports',
        blank=True
    )

    summary = models.TextField()
    blockers = models.TextField(blank=True)
    next_day_plan = models.TextField(blank=True)

    hours_worked = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Daily Report')
        verbose_name_plural = _('Daily Reports')
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date}"


class Meeting(models.Model):
    """Meeting management."""

    STATUS_CHOICES = [
        ('SCHEDULED', _('Scheduled')),
        ('IN_PROGRESS', _('In Progress')),
        ('COMPLETED', _('Completed')),
        ('CANCELLED', _('Cancelled')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='meetings',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)

    organizer = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='organized_meetings'
    )
    participants = models.ManyToManyField(
        'core_auth.TelegramUser',
        related_name='meetings',
        blank=True
    )

    meeting_link = models.URLField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.title} - {self.scheduled_at}"


class MeetingVote(models.Model):
    """Voting for meeting time slots."""

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='meeting_votes'
    )
    time_slot = models.DateTimeField()
    vote = models.BooleanField(default=True)  # True = available, False = not available

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Meeting Vote')
        verbose_name_plural = _('Meeting Votes')
        unique_together = ['meeting', 'user', 'time_slot']

    def __str__(self):
        return f"{self.user} - {self.meeting.title} - {self.time_slot}"


class Reminder(models.Model):
    """Reminders for tasks and deadlines."""

    TYPE_CHOICES = [
        ('TASK_DEADLINE', _('Task Deadline')),
        ('MEETING', _('Meeting')),
        ('DAILY_REPORT', _('Daily Report')),
        ('WEEKLY_REPORT', _('Weekly Report')),
        ('CUSTOM', _('Custom')),
    ]

    user = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='reminders'
    )
    reminder_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,
        blank=True
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,
        blank=True
    )

    message = models.TextField()
    remind_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Reminder')
        verbose_name_plural = _('Reminders')
        ordering = ['remind_at']

    def __str__(self):
        return f"{self.user} - {self.get_reminder_type_display()} - {self.remind_at}"


class LearningResource(models.Model):
    """Learning resources and documentation."""

    RESOURCE_TYPES = [
        ('ARTICLE', _('Article')),
        ('VIDEO', _('Video')),
        ('DOCUMENTATION', _('Documentation')),
        ('TUTORIAL', _('Tutorial')),
        ('BOOK', _('Book')),
        ('OTHER', _('Other')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='learning_resources',
        null=True,
        blank=True
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='learning_resources',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField(blank=True)
    file = models.FileField(upload_to='learning_resources/', blank=True)

    added_by = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='added_resources'
    )

    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Learning Resource')
        verbose_name_plural = _('Learning Resources')
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Approval(models.Model):
    """Approval workflow for tasks and projects."""

    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('APPROVED', _('Approved')),
        ('REJECTED', _('Rejected')),
        ('CANCELLED', _('Cancelled')),
    ]

    TYPE_CHOICES = [
        ('TASK', _('Task')),
        ('PROJECT', _('Project')),
        ('REPORT', _('Report')),
        ('OTHER', _('Other')),
    ]

    approval_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='approvals',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='approvals',
        null=True,
        blank=True
    )

    requested_by = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='approval_requests'
    )
    approver = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='approvals_to_review'
    )

    description = models.TextField()
    response_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Approval')
        verbose_name_plural = _('Approvals')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_approval_type_display()} - {self.status}"


class Alert(models.Model):
    """System alerts and notifications."""

    ALERT_TYPES = [
        ('TASK_ASSIGNED', _('Task Assigned')),
        ('TASK_OVERDUE', _('Task Overdue')),
        ('DEADLINE_APPROACHING', _('Deadline Approaching')),
        ('MEETING_REMINDER', _('Meeting Reminder')),
        ('APPROVAL_REQUIRED', _('Approval Required')),
        ('APPROVAL_RESPONSE', _('Approval Response')),
        ('PROJECT_UPDATE', _('Project Update')),
        ('MENTION', _('Mention')),
        ('SYSTEM', _('System')),
    ]

    PRIORITY_CHOICES = [
        ('LOW', _('Low')),
        ('MEDIUM', _('Medium')),
        ('HIGH', _('High')),
        ('URGENT', _('Urgent')),
    ]

    user = models.ForeignKey(
        'core_auth.TelegramUser',
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')

    title = models.CharField(max_length=200)
    message = models.TextField()

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='alerts',
        null=True,
        blank=True
    )

    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Alert')
        verbose_name_plural = _('Alerts')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.get_alert_type_display()}"
