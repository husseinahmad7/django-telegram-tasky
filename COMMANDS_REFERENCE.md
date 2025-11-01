# 📋 Tasky Bot - Commands Reference

Quick reference for all available bot commands.

## 🏠 Basic Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and main menu | `/start` |
| `/help` | Show all available commands | `/help` |
| `/menu` | Display main menu | `/menu` |

## 📁 Project Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/projects` | List all projects | `/projects` |
| `/myprojects` | List your projects | `/myprojects` |
| `/createproject` | Create a new project | `/createproject` |

**Interactive:**
- Click project → View details
- Click "Create Project" → Follow conversation flow

## 📝 Task Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/tasks` | List all tasks | `/tasks` |
| `/mytasks` | List your assigned tasks | `/mytasks` |
| `/createtask` | Create a new task | `/createtask` |

**Interactive:**
- Click task → View details
- Click "Update Status" → Change task status
- Click "Add Comment" → Add comment to task

## 📅 Meeting Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/meetings` | List upcoming meetings | `/meetings` |
| `/schedulemeeting` | Schedule a new meeting | `/schedulemeeting` |

**Interactive:**
- Click meeting → View details
- Click "Vote" → Vote on meeting time
- View vote results

## ✅ Approval Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/approvals` | List pending approvals | `/approvals` |
| `/requestapproval` | Request approval | `/requestapproval` |

**Interactive:**
- Click approval → View details
- Click "Approve" → Approve request
- Click "Reject" → Reject request

## 📊 Report Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/dailyreport` | Submit daily report | `/dailyreport` |
| `/weeklyreport` | View weekly summary | `/weeklyreport` |

## 🔔 Notification Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/notifications` | View all notifications | `/notifications` |
| `/reminders` | View upcoming reminders | `/reminders` |
| `/settings` | Notification preferences | `/settings` |

**Interactive:**
- Click notification → View details
- Click "Mark All Read" → Mark all as read
- Toggle notification preferences

## 👤 User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/profile` | View your profile | `/profile` |
| `/team` | View your team | `/team` |

---

## 🎯 Common Workflows

### Creating a Project

1. Send `/createproject` or click "Create Project"
2. Enter project name
3. Enter project description
4. Select deadline (or skip)
5. ✅ Project created!

### Creating a Task

1. Send `/createtask` or click "Create Task"
2. Enter task title
3. Enter task description
4. Select project
5. Select priority
6. Set deadline (optional)
7. ✅ Task created!

### Scheduling a Meeting

1. Send `/schedulemeeting`
2. Enter meeting title
3. Enter meeting description
4. Select project
5. Enter meeting time
6. ✅ Meeting scheduled!

### Requesting Approval

1. Send `/requestapproval`
2. Select approval type (Task/Project)
3. Select item to approve
4. Enter reason for approval
5. ✅ Approval request sent!

### Voting on Meeting

1. Go to `/meetings`
2. Click on a meeting
3. Click "Vote"
4. Select: Available / Not Available / Maybe
5. ✅ Vote recorded!

---

## 🎨 Button Navigation

### Main Menu Buttons

- 📁 **My Projects** → View your projects
- 📝 **My Tasks** → View your tasks
- 📅 **Meetings** → View meetings
- 🔔 **Notifications** → View notifications
- ℹ️ **Help** → Show help

### Common Buttons

- **◀️ Back** → Go back to previous screen
- **🏠 Menu** → Return to main menu
- **➕ Create** → Create new item
- **✏️ Edit** → Edit item
- **🗑️ Delete** → Delete item
- **◀️ Previous** → Previous page
- **▶️ Next** → Next page

---

## 💡 Tips & Tricks

### Quick Actions

- **Cancel anytime:** Send `/cancel` during any conversation
- **Go to menu:** Click "🏠 Menu" button or send `/menu`
- **Get help:** Send `/help` anytime

### Keyboard Shortcuts

- Type `/` to see all available commands
- Use arrow buttons for pagination
- Click inline buttons instead of typing

### Notifications

- Enable/disable in `/settings`
- Mark all as read with one click
- View notification history

### Task Management

- Filter tasks by status
- Sort by priority or deadline
- Add comments for collaboration
- Track progress with status updates

---

## 🔧 Admin Commands

(Available to admins only)

| Command | Description |
|---------|-------------|
| `/stats` | View bot statistics |
| `/users` | List all users |
| `/broadcast` | Send message to all users |

---

## 📱 Mobile Tips

### Best Practices

1. **Use buttons** instead of typing commands
2. **Enable notifications** for important updates
3. **Pin the chat** for quick access
4. **Use /menu** to navigate quickly

### Recommended Settings

- ✅ Enable task assignment notifications
- ✅ Enable deadline reminders
- ✅ Enable meeting notifications
- ⚠️ Disable general notifications (if too many)

---

## 🆘 Troubleshooting

### Command Not Working?

1. Check if you typed it correctly (with `/`)
2. Try `/help` to see available commands
3. Use buttons instead of typing
4. Restart with `/start`

### Button Not Responding?

1. Wait a few seconds (might be processing)
2. Try clicking again
3. Go back and try again
4. Send `/menu` to reset

### Not Receiving Notifications?

1. Check `/settings` - are they enabled?
2. Is Celery running? (for automatic reminders)
3. Check your Telegram notification settings

---

## 📚 Documentation

For more detailed information:

- **README.md** - Main documentation
- **QUICKSTART.md** - 5-minute setup guide
- **FEATURES_COMPLETE.md** - All features explained
- **CELERY_OPTIONAL.md** - Celery setup guide
- **TESTING_CHECKLIST.md** - Testing guide
- **DEPLOYMENT.md** - Production deployment

---

## 🎓 Learning Path

### Beginner

1. Start with `/start`
2. Create a project with `/createproject`
3. Create a task with `/createtask`
4. View your tasks with `/mytasks`

### Intermediate

1. Schedule a meeting with `/schedulemeeting`
2. Request approval with `/requestapproval`
3. Submit daily report with `/dailyreport`
4. Configure notifications in `/settings`

### Advanced

1. Use task dependencies
2. Set up team roles
3. Track project progress
4. Generate weekly reports
5. Enable Celery for automation

---

## 🚀 Quick Reference Card

**Print this for quick access:**

```
BASIC:           PROJECTS:         TASKS:
/start           /projects         /tasks
/help            /myprojects       /mytasks
/menu            /createproject    /createtask

MEETINGS:        APPROVALS:        NOTIFICATIONS:
/meetings        /approvals        /notifications
/schedulemeeting /requestapproval  /reminders
                                   /settings

REPORTS:
/dailyreport
/weeklyreport
```

---

**Need more help?** Send `/help` in the bot or check the documentation! 📖

