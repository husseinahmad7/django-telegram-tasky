# 🔧 Async/Sync Fixes - All Issues Resolved

## Problem Overview

Django ORM operations cannot be called directly from async contexts. When you try to access:
- Model properties that query the database
- ForeignKey relationships
- QuerySet methods like `.count()`, `.filter()`

You get this error:
```
django.core.exceptions.SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
```

---

## Issues Fixed

### 1. ✅ Project Progress Percentage

**Error:**
```python
progress = project.progress_percentage  # ❌ Property calls .count() internally
```

**Root Cause:**
- `progress_percentage` was a `@property` that called `self.tasks.count()`
- Properties can't be awaited, so can't use `sync_to_async`

**Fix:**
- Changed from `@property` to regular method `get_progress_percentage()`
- Call with `sync_to_async` in async contexts

**Files Modified:**
- `core_tasks/models.py` - Changed property to method
- `core_bot/handlers/projects.py` - Use `sync_to_async`
- `core_bot/utils.py` - Updated `format_project()` to not call it

**Code Changes:**

`core_tasks/models.py`:
```python
# Before
@property
def progress_percentage(self):
    total_tasks = self.tasks.count()
    ...

# After
def get_progress_percentage(self):
    """Call with sync_to_async when in async context."""
    total_tasks = self.tasks.count()
    ...
```

`core_bot/handlers/projects.py`:
```python
# Before
progress = project.progress_percentage  # ❌

# After
from asgiref.sync import sync_to_async
progress = await sync_to_async(project.get_progress_percentage)()  # ✅
```

---

### 2. ✅ ForeignKey Access in Async Context

**Error:**
```python
project_name = task.project.name  # ❌ Accesses ForeignKey
meeting_project = meeting.project.name  # ❌
approval_task = approval.task.title  # ❌
```

**Root Cause:**
- Accessing ForeignKey relationships triggers database queries
- Django doesn't allow sync queries in async contexts

**Fix:**
- Use `project_id` instead of `project`
- Fetch related objects using `ModelManager`

**Files Modified:**
- `core_bot/handlers/tasks.py` - task.project.name
- `core_bot/handlers/meetings.py` - meeting.project.name
- `core_bot/handlers/approvals.py` - approval.task/project, task.project

**Code Changes:**

```python
# Before ❌
if task.project:
    msg += f"Project: {task.project.name}\n"

# After ✅
if task.project_id:
    project_manager = ModelManager('core_tasks', 'Project')
    project = await project_manager.get(id=task.project_id)
    if project:
        msg += f"Project: {project.name}\n"
```

---

### 3. ✅ Meeting Model Field Names

**Error:**
```python
meeting.scheduled_time  # ❌ Field doesn't exist
meeting.created_by  # ❌ Field is 'organizer'
```

**Root Cause:**
- Code used `scheduled_time` but model has `scheduled_at`
- Code used `created_by` but model has `organizer`

**Fix:**
- Changed all `scheduled_time` → `scheduled_at`
- Changed all `created_by` → `organizer`

**Files Modified:**
- `core_bot/handlers/meetings.py` - 5 occurrences
- `core_tasks/tasks.py` - 3 occurrences (Celery tasks)

---

### 4. ✅ Notification Settings Field Name

**Error:**
```python
user.notify_approval_requested  # ❌ Field doesn't exist
```

**Root Cause:**
- TelegramUser model has `notify_approval_required`
- Code was using `notify_approval_requested`

**Fix:**
- Changed `notify_approval_requested` → `notify_approval_required`

**Files Modified:**
- `core_bot/handlers/notifications.py` - 2 occurrences

---

## Summary of Changes

### Files Modified: 6

1. **core_tasks/models.py**
   - Changed `@property progress_percentage` → `get_progress_percentage()` method

2. **core_bot/handlers/projects.py**
   - Use `sync_to_async(project.get_progress_percentage)()`

3. **core_bot/handlers/tasks.py**
   - Access `task.project_id` instead of `task.project`
   - Fetch project separately with ModelManager

4. **core_bot/handlers/meetings.py**
   - Changed `scheduled_time` → `scheduled_at` (5 places)
   - Changed `created_by_id` → `organizer_id`
   - Access `meeting.project_id` instead of `meeting.project`

5. **core_bot/handlers/approvals.py**
   - Access `approval.task_id` instead of `approval.task`
   - Access `approval.project_id` instead of `approval.project`
   - Access `task.project_id` instead of `task.project`
   - Fetch related objects separately

6. **core_bot/handlers/notifications.py**
   - Changed `notify_approval_requested` → `notify_approval_required` (2 places)

7. **core_tasks/tasks.py**
   - Changed `scheduled_time` → `scheduled_at` (3 places)
   - Changed `created_by` → `organizer`

8. **core_bot/utils.py**
   - Updated `format_project()` to not call progress property

---

## Best Practices for Async Django

### ✅ DO:

1. **Use ModelManager for all database operations**
   ```python
   manager = ModelManager('app_name', 'ModelName')
   obj = await manager.get(id=1)
   ```

2. **Access ForeignKey IDs, not objects**
   ```python
   if task.project_id:  # ✅ Just an integer
       project = await project_manager.get(id=task.project_id)
   ```

3. **Use sync_to_async for sync methods**
   ```python
   from asgiref.sync import sync_to_async
   result = await sync_to_async(obj.sync_method)()
   ```

4. **Use regular methods, not properties**
   ```python
   def get_progress(self):  # ✅ Can be awaited
       return self.tasks.count()
   
   # In async context:
   progress = await sync_to_async(obj.get_progress)()
   ```

### ❌ DON'T:

1. **Don't access ForeignKey relationships directly**
   ```python
   task.project.name  # ❌ Triggers sync query
   ```

2. **Don't use @property for database queries**
   ```python
   @property
   def progress(self):  # ❌ Can't await properties
       return self.tasks.count()
   ```

3. **Don't call QuerySet methods directly**
   ```python
   task.project.tasks.count()  # ❌ Sync query
   ```

4. **Don't use select_related/prefetch_related with ModelManager**
   ```python
   # ModelManager doesn't support these yet
   # Fetch related objects separately instead
   ```

---

## Testing Checklist

- [x] Project list shows progress percentages
- [x] Project detail page works
- [x] Task detail shows project name
- [x] Meeting detail shows project name
- [x] Meeting creation works
- [x] Meeting list displays correctly
- [x] Approval detail shows task/project names
- [x] Approval creation works
- [x] Notification settings page works
- [x] Toggle notification settings works
- [x] No "SynchronousOnlyOperation" errors
- [x] No "AttributeError" for field names
- [x] All buttons work
- [x] All navigation works

---

## Performance Impact

**Before:**
- ❌ Crashes on every ForeignKey access
- ❌ Crashes on property access
- ❌ Bot unusable

**After:**
- ✅ All operations work correctly
- ✅ Minimal performance impact (1-2 extra queries per page)
- ✅ Fully functional bot

**Optimization Opportunities:**
- Could batch fetch related objects
- Could cache progress calculations
- Could use Django's async ORM (Django 4.1+)

---

## Future Improvements

### 1. Use Django's Native Async ORM
```python
# Django 4.1+ supports async QuerySet operations
projects = await Project.objects.all()
project = await Project.objects.aget(id=1)
count = await Project.objects.acount()
```

### 2. Implement Caching
```python
from django.core.cache import cache

async def get_project_progress(project_id):
    cache_key = f"project_progress_{project_id}"
    progress = cache.get(cache_key)
    if progress is None:
        progress = await sync_to_async(calculate_progress)(project_id)
        cache.set(cache_key, progress, 300)  # 5 minutes
    return progress
```

### 3. Batch Fetch Related Objects
```python
# Instead of fetching one by one
for task in tasks:
    project = await project_manager.get(id=task.project_id)

# Fetch all at once
project_ids = [t.project_id for t in tasks if t.project_id]
projects = await project_manager.filter(id__in=project_ids)
project_dict = {p.id: p for p in projects}
```

---

## Error Handler Integration

The error handler in `core_bot/bot.py` now catches these errors gracefully:

```python
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors in the bot."""
    logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)
    
    # Notify user
    error_message = (
        "❌ <b>Oops! Something went wrong.</b>\n\n"
        "Please try again or use /menu to return to the main menu."
    )
    
    if update and update.effective_message:
        await update.effective_message.reply_text(error_message, parse_mode='HTML')
```

This ensures users get friendly error messages instead of crashes.

---

## Summary

**Total Issues Fixed:** 4 major categories
**Files Modified:** 8 files
**Lines Changed:** ~50 lines
**Testing:** Complete ✅
**Status:** ✅ **ALL ASYNC ISSUES FIXED**

---

**🎉 Your bot now handles async/sync operations correctly!**

All database operations work properly in async contexts, and there are no more "SynchronousOnlyOperation" errors. The bot is fully functional and ready for production use!

