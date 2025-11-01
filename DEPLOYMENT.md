# 🚀 Deployment Guide

Production deployment guide for Tasky bot.

## Deployment Options

### Option 1: VPS/Cloud Server (Recommended)

#### Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Python 3.14 (or 3.12+)
- 1GB RAM minimum
- Domain name with SSL certificate
- PostgreSQL (optional, recommended for production)

#### Step-by-Step

1. **Setup Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.14 (or use deadsnakes PPA for 3.12)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.14 python3.14-venv python3.14-dev

# Install system dependencies
sudo apt install nginx postgresql postgresql-contrib redis-server
```

2. **Clone Project**
```bash
cd /var/www
sudo git clone <your-repo-url> tasky
cd tasky
sudo chown -R $USER:$USER /var/www/tasky
```

3. **Setup Virtual Environment**
```bash
python3.14 -m venv venv
source venv/bin/activate
pip install uv
uv pip install -r requirements.txt
```

4. **Configure Environment**
```bash
# Create .env file
nano .env
```

```env
# Production settings
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/tasky

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
WEBHOOK_URL=https://yourdomain.com

# Optional
GEMINI_API_KEY=your_gemini_key

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

5. **Setup PostgreSQL**
```bash
sudo -u postgres psql

CREATE DATABASE tasky;
CREATE USER tasky_user WITH PASSWORD 'your_password';
ALTER ROLE tasky_user SET client_encoding TO 'utf8';
ALTER ROLE tasky_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tasky_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE tasky TO tasky_user;
\q
```

Update `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tasky',
        'USER': 'tasky_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

6. **Run Migrations**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

7. **Setup Nginx**
```bash
sudo nano /etc/nginx/sites-available/tasky
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/tasky/static/;
    }

    location /media/ {
        alias /var/www/tasky/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/tasky /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

8. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

9. **Setup Systemd Service**
```bash
sudo nano /etc/systemd/system/tasky.service
```

```ini
[Unit]
Description=Tasky Telegram Bot
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/tasky
Environment="PATH=/var/www/tasky/venv/bin"
ExecStart=/var/www/tasky/venv/bin/gunicorn Tasky.asgi:app \
    -k uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/tasky/access.log \
    --error-logfile /var/log/tasky/error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/tasky
sudo chown www-data:www-data /var/log/tasky

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tasky
sudo systemctl start tasky
sudo systemctl status tasky
```

10. **Setup Celery (Optional)**
```bash
sudo nano /etc/systemd/system/tasky-celery.service
```

```ini
[Unit]
Description=Tasky Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/tasky
Environment="PATH=/var/www/tasky/venv/bin"
ExecStart=/var/www/tasky/venv/bin/celery -A Tasky worker -l info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tasky-celery
sudo systemctl start tasky-celery
```

11. **Set Webhook**
```bash
source venv/bin/activate
python manage.py set_webhook https://yourdomain.com
```

### Option 2: Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD python manage.py migrate && \
    gunicorn Tasky.asgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: tasky
      POSTGRES_USER: tasky
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: gunicorn Tasky.asgi:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    build: .
    command: celery -A Tasky worker -l info
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

3. **Deploy**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py set_webhook https://yourdomain.com
```

### Option 3: Heroku

1. **Create Procfile**
```
web: gunicorn Tasky.asgi:app -k uvicorn.workers.UvicornWorker
worker: celery -A Tasky worker -l info
```

2. **Create runtime.txt**
```
python-3.12.0
```

3. **Deploy**
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set SECRET_KEY=your_secret_key
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py set_webhook https://your-app-name.herokuapp.com
```

## Post-Deployment

### Monitoring

1. **Check Logs**
```bash
# Systemd
sudo journalctl -u tasky -f

# Docker
docker-compose logs -f web

# Heroku
heroku logs --tail
```

2. **Monitor Performance**
```bash
# Server resources
htop

# Database
sudo -u postgres psql tasky
SELECT * FROM pg_stat_activity;

# Nginx
sudo tail -f /var/log/nginx/access.log
```

### Backup

1. **Database Backup**
```bash
# PostgreSQL
pg_dump tasky > backup_$(date +%Y%m%d).sql

# Automated backup script
sudo nano /usr/local/bin/backup-tasky.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/tasky"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump tasky > $BACKUP_DIR/tasky_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

```bash
sudo chmod +x /usr/local/bin/backup-tasky.sh

# Add to crontab
sudo crontab -e
0 2 * * * /usr/local/bin/backup-tasky.sh
```

### Security

1. **Firewall**
```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

2. **Fail2Ban**
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

3. **Regular Updates**
```bash
sudo apt update && sudo apt upgrade -y
```

## Troubleshooting

### Bot Not Responding
1. Check webhook: `python manage.py shell` → check webhook info
2. Check logs: `sudo journalctl -u tasky -f`
3. Verify bot token in `.env`
4. Test webhook URL is accessible

### Database Issues
1. Check PostgreSQL is running: `sudo systemctl status postgresql`
2. Verify credentials in `.env`
3. Check migrations: `python manage.py showmigrations`

### Performance Issues
1. Increase workers: Edit systemd service
2. Enable caching: Add Redis caching
3. Optimize database: Add indexes
4. Use CDN for static files

## Maintenance

### Updates
```bash
cd /var/www/tasky
git pull
source venv/bin/activate
uv pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart tasky
```

### Scaling
- Add more workers in systemd service
- Use load balancer for multiple servers
- Separate database server
- Use CDN for static files
- Implement caching layer

---

**Production Checklist**:
- [ ] SSL certificate installed
- [ ] DEBUG=False in settings
- [ ] SECRET_KEY is secure and unique
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Firewall configured
- [ ] Logs rotation configured
- [ ] Webhook set to production URL
- [ ] Admin account created
- [ ] Default roles created
- [ ] Error tracking setup (Sentry)

