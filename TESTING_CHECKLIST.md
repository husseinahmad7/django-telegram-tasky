# 🧪 Testing Checklist

Complete testing guide for Tasky bot MVP.

## Pre-Testing Setup

- [ ] Python 3.14 (or 3.12+) installed
- [ ] Dependencies installed (`uv pip install -r requirements.txt`)
- [ ] `.env` configured with `TELEGRAM_BOT_TOKEN`
- [ ] Database migrated (`python manage.py migrate`)
- [ ] Superuser created
- [ ] Default roles created
- [ ] ngrok installed and running
- [ ] Webhook set correctly

## 🚀 Startup Tests

### Automated Startup
- [ ] Run `python start_bot.py`
- [ ] ngrok starts automatically
- [ ] Webhook is set successfully
- [ ] Server starts on port 8000
- [ ] No errors in console

### Manual Startup
- [ ] ngrok starts: `ngrok http 8000`
- [ ] Webhook sets: `python manage.py set_webhook <url>`
- [ ] Server starts: `uvicorn Tasky.asgi:app --reload`
- [ ] Webhook info shows correct URL

## 📱 Basic Bot Tests

### Initial Connection
- [ ] Bot responds to `/start`
- [ ] Welcome message displays correctly
- [ ] Main menu appears with inline buttons
- [ ] User is created in database

### Help System
- [ ] `/help` shows all commands
- [ ] Help text is formatted correctly
- [ ] All command categories listed
- [ ] Help button in menu works

### Menu Navigation
- [ ] `/menu` displays main menu
- [ ] All menu buttons are clickable
- [ ] Menu callback works from inline buttons
- [ ] Back buttons work correctly

## 📁 Project Management Tests

### List Projects
- [ ] `/projects` shows empty state when no projects
- [ ] "Create Project" button appears
- [ ] After creating projects, list displays correctly
- [ ] Pagination works (if >5 projects)
- [ ] Progress percentage shows correctly
- [ ] Status emoji displays

### Create Project
- [ ] `/createproject` starts conversation
- [ ] "Create Project" button starts conversation
- [ ] Name prompt appears
- [ ] Description prompt appears (skippable)
- [ ] Priority selection shows 4 options
- [ ] Project is created in database
- [ ] Success message displays
- [ ] Can view created project
- [ ] `/cancel` cancels creation

### Project Detail
- [ ] Click on project shows details
- [ ] Project name and description display
- [ ] Statistics show (total tasks, done, in progress, todo)
- [ ] Action buttons appear (Tasks, Meetings, Reports, Resources)
- [ ] "Add Task" button works
- [ ] Back button returns to project list

## 📝 Task Management Tests

### List Tasks
- [ ] `/tasks` shows empty state when no tasks
- [ ] `/mytasks` filters user's tasks
- [ ] Task list displays with status emoji
- [ ] Priority emoji shows
- [ ] Overdue tasks show warning (⚠️)
- [ ] Pagination works (if >5 tasks)
- [ ] Filter buttons work (All/My Tasks)

### Create Task
- [ ] `/createtask` starts conversation
- [ ] "Add Task" from project works
- [ ] Title prompt appears
- [ ] Description prompt appears (skippable)
- [ ] Priority selection shows 4 options
- [ ] Deadline prompt appears (skippable)
- [ ] Valid date format accepted (YYYY-MM-DD HH:MM)
- [ ] Invalid date shows error
- [ ] Task is created in database
- [ ] Task linked to correct project
- [ ] Success message displays

### Task Detail
- [ ] Click on task shows details
- [ ] Task title and description display
- [ ] Project name shows
- [ ] Status displays correctly
- [ ] Created date shows
- [ ] Estimated/actual hours show (if set)
- [ ] Status update buttons appear
- [ ] Assign button appears
- [ ] Comments button appears

### Update Task Status
- [ ] "Done" button updates status
- [ ] "In Progress" button updates status
- [ ] "Review" button updates status
- [ ] "Blocked" button updates status
- [ ] Success message appears
- [ ] Task detail refreshes with new status
- [ ] Database updates correctly

### Task Assignment
- [ ] "Assign" button shows message
- [ ] Placeholder message displays
- [ ] (Full implementation pending)

## 📊 Reports Tests

### Daily Report
- [ ] `/dailyreport` shows instructions
- [ ] Format guide displays
- [ ] (Full implementation pending)

### Weekly Report
- [ ] `/weeklyreport` shows placeholder
- [ ] Coming soon message displays
- [ ] (Full implementation pending)

## 📅 Meeting Tests

### List Meetings
- [ ] `/meetings` shows placeholder
- [ ] Coming soon message displays
- [ ] (Full implementation pending)

### Schedule Meeting
- [ ] `/schedulemeeting` shows placeholder
- [ ] (Full implementation pending)

### Meeting Vote
- [ ] `/meetingvote` shows placeholder
- [ ] (Full implementation pending)

## ✅ Approval Tests

### Request Approval
- [ ] `/requestapproval` shows placeholder
- [ ] (Full implementation pending)

### Approve/Reject
- [ ] `/approve` shows placeholder
- [ ] `/reject` shows placeholder
- [ ] (Full implementation pending)

## 🗄️ Database Tests

### Django Admin
- [ ] Access admin at `/django/admin/`
- [ ] Login with superuser
- [ ] All models appear in admin
- [ ] TelegramUser model shows users
- [ ] Projects can be created/edited
- [ ] Tasks can be created/edited
- [ ] Roles can be managed
- [ ] All relationships work

### Data Integrity
- [ ] User created on first bot interaction
- [ ] Telegram ID stored correctly
- [ ] Projects link to owner
- [ ] Tasks link to project
- [ ] Tasks link to creator
- [ ] Roles can be assigned
- [ ] Permissions work correctly

## 🎨 UI/UX Tests

### Visual Elements
- [ ] Emojis display correctly
- [ ] Status badges show
- [ ] Priority indicators work
- [ ] Progress percentages accurate
- [ ] Formatting is consistent

### Navigation
- [ ] All back buttons work
- [ ] Pagination buttons work
- [ ] Menu navigation is intuitive
- [ ] No dead-end screens
- [ ] Can always return to menu

### Responsiveness
- [ ] Bot responds quickly (<2s)
- [ ] No timeout errors
- [ ] Webhook processes updates
- [ ] No duplicate messages
- [ ] Callbacks acknowledge

## 🔧 Error Handling Tests

### Invalid Input
- [ ] Invalid date format handled
- [ ] Missing required fields handled
- [ ] Invalid callback data handled
- [ ] Unknown commands handled

### Edge Cases
- [ ] Empty project list handled
- [ ] Empty task list handled
- [ ] No assigned tasks handled
- [ ] Deleted items handled gracefully

### Network Issues
- [ ] Webhook failures logged
- [ ] Retry mechanism works
- [ ] Error messages user-friendly

## 🔐 Security Tests

### Authentication
- [ ] Only Telegram users can interact
- [ ] User data isolated
- [ ] Telegram ID verified

### Permissions
- [ ] Role permissions respected
- [ ] Users can't access others' data
- [ ] Admin functions protected

## 📊 Performance Tests

### Load Testing
- [ ] Multiple users can interact simultaneously
- [ ] Database queries optimized
- [ ] No memory leaks
- [ ] Server handles concurrent requests

### Scalability
- [ ] Pagination prevents overload
- [ ] Large datasets handled
- [ ] Response times acceptable

## 🐛 Known Issues

Document any issues found:

1. **Issue**: 
   - **Severity**: 
   - **Steps to Reproduce**: 
   - **Expected**: 
   - **Actual**: 
   - **Status**: 

## ✅ Sign-Off

### MVP Features Complete
- [x] Basic bot commands
- [x] Project management
- [x] Task management
- [x] Modern UI with inline keyboards
- [x] Pagination
- [x] Database models
- [x] Admin interface
- [x] Documentation

### Pending Features (Post-MVP)
- [ ] Meeting voting
- [ ] Approval workflow
- [ ] File attachments
- [ ] Reminder notifications
- [ ] AI integration
- [ ] Advanced reporting

## 📝 Test Results

**Date**: ___________
**Tester**: ___________
**Version**: MVP 1.0
**Status**: ⬜ Pass / ⬜ Fail / ⬜ Partial

**Notes**:
_______________________________________
_______________________________________
_______________________________________

**Blockers**:
_______________________________________
_______________________________________

**Ready for Production**: ⬜ Yes / ⬜ No

---

**Next Steps After Testing**:
1. Fix any critical bugs
2. Implement pending features
3. Performance optimization
4. User acceptance testing
5. Production deployment

