# 🔔 Celery - Optional Feature

Celery is **completely optional** in Tasky. The bot works perfectly fine without it!

## What is Celery?

Celery is a background task processor that enables:
- ⏰ Automatic deadline reminders
- 📅 Meeting reminders
- 🔔 Scheduled notifications
- 📊 Daily report reminders
- 🧹 Automatic cleanup of old data

## Running WITHOUT Celery (Default)

### ✅ What Works
Everything except automatic background tasks:
- ✅ All bot commands
- ✅ Project management
- ✅ Task management
- ✅ Meeting management
- ✅ Approval workflow
- ✅ Manual notifications
- ✅ All interactive features

### ❌ What Doesn't Work
Only automatic scheduled tasks:
- ❌ Automatic deadline reminders
- ❌ Automatic meeting reminders
- ❌ Automatic overdue alerts
- ❌ Scheduled daily report reminders

### How to Run
Just start the bot normally:
```bash
python start_bot.py
```

That's it! No additional setup needed.

## Running WITH Celery (Optional)

If you want automatic reminders and notifications:

### 1. Install Dependencies
```bash
pip install celery redis
```

Or add to your requirements:
```txt
celery>=5.3.0
redis>=5.0.0
```

### 2. Install and Start Redis

**Windows:**
```bash
# Download Redis from: https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker
docker run -d -p 6379:6379 redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**macOS:**
```bash
brew install redis
brew services start redis
```

### 3. Start Celery Worker

Open a new terminal:
```bash
celery -A Tasky worker -l info
```

### 4. Start Celery Beat (Scheduler)

Open another terminal:
```bash
celery -A Tasky beat -l info
```

### 5. Start the Bot

In your main terminal:
```bash
python start_bot.py
```

Now you have:
- ✅ Bot running (main process)
- ✅ Celery worker (processes tasks)
- ✅ Celery beat (schedules tasks)

## Scheduled Tasks (When Celery is Enabled)

| Task | Schedule | Description |
|------|----------|-------------|
| Deadline Reminders | Every hour | Reminds users of tasks due in 24h |
| Overdue Alerts | Every 6 hours | Alerts for overdue tasks |
| Meeting Reminders | Every 30 min | Reminds 30min before meetings |
| Process Reminders | Every 5 min | Sends pending reminders |
| Daily Report Reminder | 5 PM daily | Reminds to submit daily report |
| Cleanup | 2 AM daily | Removes old notifications |

## Configuration

### Environment Variables

```env
# Optional - only needed if using Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

If not set, defaults to `redis://localhost:6379/0`

### Custom Redis URL

If Redis is on a different host/port:
```env
CELERY_BROKER_URL=redis://your-redis-host:6379/0
```

## Troubleshooting

### "Celery not found" Error
**Solution:** Celery is optional. The bot will work without it.

If you see this in logs, it's just informational - not an error.

### Redis Connection Error
**When:** Only if you installed Celery but Redis isn't running

**Solution:**
1. Start Redis: `redis-server`
2. Or uninstall Celery: `pip uninstall celery redis`

### Tasks Not Running
**Check:**
1. Is Redis running? `redis-cli ping` (should return "PONG")
2. Is Celery worker running? Check the worker terminal
3. Is Celery beat running? Check the beat terminal

## Production Deployment

### Option 1: Without Celery (Simpler)
```bash
# Just run the bot
python start_bot.py
```

**Pros:**
- ✅ Simpler setup
- ✅ Fewer dependencies
- ✅ Less resource usage
- ✅ Easier to maintain

**Cons:**
- ❌ No automatic reminders

### Option 2: With Celery (Full Features)
```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A Tasky worker -l info

# Terminal 3: Celery Beat
celery -A Tasky beat -l info

# Terminal 4: Bot
python start_bot.py
```

**Pros:**
- ✅ Full automation
- ✅ Automatic reminders
- ✅ Better user experience

**Cons:**
- ❌ More complex setup
- ❌ More dependencies
- ❌ More resource usage

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/tasky.conf`:

```ini
[program:tasky-bot]
command=/path/to/venv/bin/python start_bot.py
directory=/path/to/Tasky
user=tasky
autostart=true
autorestart=true

[program:tasky-worker]
command=/path/to/venv/bin/celery -A Tasky worker -l info
directory=/path/to/Tasky
user=tasky
autostart=true
autorestart=true

[program:tasky-beat]
command=/path/to/venv/bin/celery -A Tasky beat -l info
directory=/path/to/Tasky
user=tasky
autostart=true
autorestart=true
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  bot:
    build: .
    command: python start_bot.py
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  worker:
    build: .
    command: celery -A Tasky worker -l info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  beat:
    build: .
    command: celery -A Tasky beat -l info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
```

## Monitoring Celery

### Flower (Web UI)

```bash
pip install flower
celery -A Tasky flower
```

Open http://localhost:5555 to see:
- Active tasks
- Task history
- Worker status
- Task statistics

### Command Line

```bash
# List active tasks
celery -A Tasky inspect active

# List scheduled tasks
celery -A Tasky inspect scheduled

# Worker stats
celery -A Tasky inspect stats
```

## FAQ

**Q: Do I need Celery?**
A: No! The bot works great without it. Only install if you want automatic reminders.

**Q: Can I add Celery later?**
A: Yes! Just install it and start the workers. No code changes needed.

**Q: Does the executable support Celery?**
A: Yes, but you'll need Redis running separately.

**Q: What if Redis crashes?**
A: The bot continues working. Only background tasks are affected.

**Q: Can I use a different broker?**
A: Yes! Celery supports RabbitMQ, Amazon SQS, etc. Update `CELERY_BROKER_URL`.

**Q: How much memory does Celery use?**
A: ~50-100MB per worker. Minimal impact.

**Q: Can I run multiple workers?**
A: Yes! For better performance:
```bash
celery -A Tasky worker -l info --concurrency=4
```

---

## Recommendation

### For Development/Testing
**Don't use Celery** - simpler and faster to iterate

### For Personal Use
**Don't use Celery** - manual reminders are fine

### For Team/Production Use
**Use Celery** - automatic reminders improve UX

---

**Bottom Line:** Celery is a nice-to-have, not a must-have. Start without it, add it later if needed! 🚀

