from django.contrib import admin
from .models import (
    Project, Task, TaskComment, TaskAttachment, DailyReport,
    Meeting, MeetingVote, Reminder, LearningResource, Approval, Alert
)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'priority', 'owner', 'progress', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
    filter_horizontal = ['members']

    def progress(self, obj):
        """Display progress percentage."""
        return f"{obj.get_progress_percentage()}%"
    progress.short_description = 'Progress'


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assigned_to', 'deadline', 'is_overdue']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    filter_horizontal = ['depends_on']


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'task__title']


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'task', 'uploaded_by', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['file_name', 'task__title']


@admin.register(DailyReport)
class DailyReportAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'date', 'hours_worked', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['user__username', 'summary']
    date_hierarchy = 'date'


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'scheduled_at', 'organizer', 'duration_minutes']
    list_filter = ['status', 'scheduled_at']
    search_fields = ['title', 'description']
    filter_horizontal = ['participants']


@admin.register(MeetingVote)
class MeetingVoteAdmin(admin.ModelAdmin):
    list_display = ['meeting', 'user', 'time_slot', 'vote']
    list_filter = ['vote', 'created_at']


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['user', 'reminder_type', 'remind_at', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'remind_at']
    search_fields = ['message', 'user__username']


@admin.register(LearningResource)
class LearningResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'project', 'task', 'added_by', 'created_at']
    list_filter = ['resource_type', 'created_at']
    search_fields = ['title', 'description', 'tags']


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['approval_type', 'status', 'requested_by', 'approver', 'created_at', 'responded_at']
    list_filter = ['approval_type', 'status', 'created_at']
    search_fields = ['description']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['user', 'alert_type', 'priority', 'is_read', 'is_sent', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_read', 'is_sent', 'created_at']
    search_fields = ['title', 'message', 'user__username']
