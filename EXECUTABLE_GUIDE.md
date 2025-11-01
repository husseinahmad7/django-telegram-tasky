# 📦 Executable Build Guide

Guide for building and distributing Tasky as a standalone executable.

## Why Build an Executable?

Building Tasky as an executable allows you to:
- ✅ Run without Python installation
- ✅ Distribute to non-technical users
- ✅ Deploy on machines without development tools
- ✅ Package all dependencies in one file

## Prerequisites

### For Building
- Python 3.12+ installed
- All project dependencies installed
- PyInstaller (`pip install pyinstaller`)
- ~500MB free disk space

### For Running (End Users)
- No Python required!
- Just the executable + .env file
- ngrok (optional, for local testing)

## Building the Executable

### Method 1: Automated Build Script (Recommended)

```bash
python build_executable.py
```

This script will:
1. Check for PyInstaller
2. Clean previous builds
3. Build the executable
4. Show you the output location

### Method 2: Manual Build

```bash
# Install PyInstaller
pip install pyinstaller

# Clean previous builds
rm -rf build dist

# Build
pyinstaller tasky.spec --clean
```

### Build Output

After successful build:
```
dist/
  └── Tasky.exe (Windows) or Tasky (Linux/Mac)
```

Size: ~50-100MB (includes all dependencies)

## Distributing the Executable

### What to Include

Create a distribution package with:

```
Tasky-Distribution/
  ├── Tasky.exe (or Tasky)
  ├── .env.example
  ├── README.txt
  └── ngrok.exe (optional)
```

### .env.example

```env
# Telegram Bot Token (required)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Webhook URL (optional - leave empty to use ngrok)
WEBHOOK_URL=

# Gemini API Key (optional)
GEMINI_API_KEY=your_gemini_key_here

# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
```

### README.txt for End Users

```
Tasky Bot - Quick Start
=======================

1. Rename .env.example to .env
2. Edit .env and add your TELEGRAM_BOT_TOKEN
3. Double-click Tasky.exe to start
4. The bot will automatically:
   - Start ngrok (if no WEBHOOK_URL set)
   - Set the webhook
   - Start the server
5. Open Telegram and send /start to your bot

Requirements:
- Internet connection
- Telegram bot token (get from @BotFather)

Troubleshooting:
- If ngrok fails, set WEBHOOK_URL in .env
- Check firewall settings
- Make sure port 8000 is available
```

## Running the Executable

### First Time Setup

1. **Get Bot Token**
   ```
   - Open Telegram
   - Message @BotFather
   - Create new bot
   - Copy the token
   ```

2. **Configure .env**
   ```bash
   # Create .env file
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   ```

3. **Run**
   ```bash
   # Windows
   Tasky.exe

   # Linux/Mac
   chmod +x Tasky
   ./Tasky
   ```

### Subsequent Runs

Just double-click the executable!

## Advanced Configuration

### Using Custom Webhook URL

If you have a server with a domain:

```env
WEBHOOK_URL=https://yourdomain.com
```

The executable will use this instead of ngrok.

### Database Location

The executable creates `db.sqlite3` in the same directory.

To use a different location:
```env
DATABASE_URL=sqlite:///path/to/your/database.db
```

### Running as a Service

#### Windows Service

Use NSSM (Non-Sucking Service Manager):

```bash
# Download NSSM
# Install service
nssm install Tasky "C:\path\to\Tasky.exe"
nssm start Tasky
```

#### Linux Systemd

Create `/etc/systemd/system/tasky.service`:

```ini
[Unit]
Description=Tasky Telegram Bot
After=network.target

[Service]
Type=simple
User=tasky
WorkingDirectory=/opt/tasky
ExecStart=/opt/tasky/Tasky
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable tasky
sudo systemctl start tasky
```

## Troubleshooting

### Build Issues

**Error: Module not found**
```bash
# Add to hiddenimports in tasky.spec
hiddenimports = [..., 'missing_module']
```

**Error: File not found**
```bash
# Add to datas in tasky.spec
datas = [..., ('path/to/file', 'destination')]
```

**Large executable size**
```bash
# Exclude unnecessary packages
excludes = ['matplotlib', 'numpy', 'pandas']
```

### Runtime Issues

**Error: No module named 'django'**
- Rebuild with all dependencies installed
- Check hiddenimports in tasky.spec

**Error: Database locked**
- Close other instances
- Check file permissions

**Error: Port 8000 already in use**
- Change port in settings
- Or kill the process using port 8000

**ngrok not starting**
- Download ngrok separately
- Place in same directory as executable
- Or set WEBHOOK_URL in .env

## Optimization

### Reduce Size

1. **Use UPX compression** (already enabled)
2. **Exclude unused modules**:
   ```python
   excludes = [
       'matplotlib',
       'numpy',
       'pandas',
       'scipy',
       'PIL',
   ]
   ```

3. **One-folder mode** (smaller but multiple files):
   ```bash
   pyinstaller tasky.spec --onedir
   ```

### Improve Startup Time

1. **Lazy imports** in code
2. **Reduce hidden imports**
3. **Use --noupx** if UPX causes issues

## Security Considerations

### For Distribution

⚠️ **Never include**:
- Your actual .env file
- Your bot token
- Your database with real data
- API keys

✅ **Always include**:
- .env.example (template)
- README with setup instructions
- License file

### For Production

1. **Use environment variables** instead of .env
2. **Set DEBUG=False**
3. **Use strong SECRET_KEY**
4. **Enable HTTPS** for webhook
5. **Regular updates** for security patches

## Platform-Specific Notes

### Windows

- Executable: `Tasky.exe`
- Antivirus may flag it (false positive)
- Add exception if needed
- Works on Windows 10/11

### Linux

- Executable: `Tasky`
- Make executable: `chmod +x Tasky`
- May need `libpython3.x.so`
- Tested on Ubuntu 20.04+

### macOS

- Executable: `Tasky`
- May need to allow in Security settings
- Right-click → Open (first time)
- Tested on macOS 11+

## CI/CD Integration

### GitHub Actions

```yaml
name: Build Executable

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, ubuntu-latest, macos-latest]
    
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: python build_executable.py
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: tasky-${{ matrix.os }}
          path: dist/
```

## Updates and Maintenance

### Updating the Executable

1. Pull latest code
2. Install new dependencies
3. Rebuild: `python build_executable.py`
4. Test thoroughly
5. Distribute new version

### Version Management

Add version to executable name:
```python
# In tasky.spec
name='Tasky-v1.0.0'
```

### Auto-Update (Advanced)

Implement update checker in code:
```python
# Check for updates on startup
# Download new version
# Replace executable
# Restart
```

## FAQ

**Q: Can I run multiple instances?**
A: Yes, but use different ports and databases.

**Q: Does it work offline?**
A: No, requires internet for Telegram API.

**Q: Can I customize the executable?**
A: Yes, edit tasky.spec and rebuild.

**Q: How do I add an icon?**
A: Set `icon='path/to/icon.ico'` in tasky.spec.

**Q: Is it safe to distribute?**
A: Yes, but don't include sensitive data.

---

**Need Help?**
- Check logs in console
- Review error messages
- Consult PyInstaller docs
- Open an issue on GitHub

