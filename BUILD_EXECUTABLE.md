# 🚀 Building Tasky Bot as Executable

## Overview

This guide shows you how to build Tasky bot as a standalone Windows executable (.exe) that:
- ✅ Runs without Python installed
- ✅ Loads `.env` from the same directory as the .exe
- ✅ Creates `db.sqlite3` in the same directory as the .exe
- ✅ Works with ngrok for webhooks
- ✅ No need to install dependencies

---

## Prerequisites

1. **Python 3.12+** installed (for building only)
2. **UV package manager** (already installed)
3. **PyInstaller** for building executables

---

## Step 1: Install PyInstaller

```bash
uv pip install pyinstaller
```

---

## Step 2: Create PyInstaller Spec File

Create a file named `tasky.spec` in the project root:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['start_bot.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include Django templates and static files
        ('core_auth', 'core_auth'),
        ('core_bot', 'core_bot'),
        ('core_tasks', 'core_tasks'),
        ('Tasky', 'Tasky'),
        # Include migrations
        ('core_auth/migrations', 'core_auth/migrations'),
        ('core_bot/migrations', 'core_bot/migrations'),
        ('core_tasks/migrations', 'core_tasks/migrations'),
    ],
    hiddenimports=[
        'django',
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'core_auth',
        'core_bot',
        'core_tasks',
        'telegram',
        'telegram.ext',
        'uvicorn',
        'starlette',
        'asgiref',
        'dotenv',
        'requests',
        'pyngrok',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tasky',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add your icon path here if you have one
)
```

---

## Step 3: Build the Executable

```bash
pyinstaller tasky.spec
```

This will create:
- `dist/Tasky.exe` - Your standalone executable
- `build/` - Temporary build files (can be deleted)

---

## Step 4: Prepare Distribution Folder

Create a folder for distribution with these files:

```
Tasky_Distribution/
├── Tasky.exe          # The executable
├── .env               # Configuration file
├── db.sqlite3         # Database (created on first run)
└── README.txt         # User instructions
```

### Create .env File

Create a `.env` file in the same directory as `Tasky.exe`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Webhook URL (if not using ngrok)
# WEBHOOK_URL=https://your-domain.com

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
```

### Create README.txt

```txt
Tasky Bot - Telegram Project Manager
====================================

SETUP INSTRUCTIONS:

1. Install ngrok (for webhook):
   - Download from: https://ngrok.com/download
   - Extract and add to PATH

2. Configure .env file:
   - Open .env in a text editor
   - Set TELEGRAM_BOT_TOKEN to your bot token
   - Save the file

3. Run Tasky.exe:
   - Double-click Tasky.exe
   - Wait for "Bot is ready!" message
   - Send /start to your bot on Telegram

REQUIREMENTS:
- Windows 10/11
- Internet connection
- ngrok installed (for automatic webhook setup)

TROUBLESHOOTING:
- If bot doesn't start, check .env file
- If webhook fails, install ngrok
- Database (db.sqlite3) is created automatically

For support, visit: https://github.com/your-repo
```

---

## Step 5: Test the Executable

1. **Copy files to test directory:**
   ```
   mkdir test_dist
   copy dist\Tasky.exe test_dist\
   copy .env test_dist\
   ```

2. **Run the executable:**
   ```
   cd test_dist
   Tasky.exe
   ```

3. **Verify:**
   - ✅ Loads .env from current directory
   - ✅ Creates db.sqlite3 in current directory
   - ✅ Starts ngrok automatically
   - ✅ Sets webhook successfully
   - ✅ Bot responds to /start

---

## Common Issues and Solutions

### Issue 1: "No module named 'django'"

**Solution:** Add to `hiddenimports` in spec file:
```python
hiddenimports=[
    'django.core.management',
    'django.core.management.commands',
    # ... other imports
]
```

### Issue 2: "Template not found"

**Solution:** Make sure templates are included in `datas`:
```python
datas=[
    ('core_auth/templates', 'core_auth/templates'),
    ('core_bot/templates', 'core_bot/templates'),
]
```

### Issue 3: ".env not found"

**Solution:** The .env file must be in the same directory as Tasky.exe, not inside the exe.

### Issue 4: "Database is locked"

**Solution:** Close any other instances of the bot or Django admin.

### Issue 5: "ngrok not found"

**Solution:** Install ngrok and add to PATH, or set WEBHOOK_URL in .env manually.

---

## Advanced: One-File Executable

To create a single .exe file (slower startup, but easier to distribute):

```python
# In tasky.spec, change EXE section:
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tasky',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,  # Add this line
)
```

---

## Distribution Checklist

Before distributing to users:

- [ ] Test executable on clean Windows machine
- [ ] Verify .env is loaded correctly
- [ ] Verify database is created
- [ ] Test all bot commands
- [ ] Test ngrok integration
- [ ] Create user documentation
- [ ] Include .env.example file
- [ ] Test without Python installed
- [ ] Test with antivirus enabled
- [ ] Create installer (optional)

---

## Creating an Installer (Optional)

Use **Inno Setup** to create a professional installer:

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create installer script (tasky_installer.iss)
3. Build installer

Example Inno Setup script:

```iss
[Setup]
AppName=Tasky Bot
AppVersion=1.0
DefaultDirName={pf}\Tasky
DefaultGroupName=Tasky
OutputDir=installer
OutputBaseFilename=TaskySetup

[Files]
Source: "dist\Tasky.exe"; DestDir: "{app}"
Source: ".env.example"; DestDir: "{app}"; DestName: ".env"

[Icons]
Name: "{group}\Tasky Bot"; Filename: "{app}\Tasky.exe"
Name: "{group}\Uninstall Tasky"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\Tasky.exe"; Description: "Launch Tasky Bot"; Flags: postinstall nowait skipifsilent
```

---

## File Structure After Build

```
Tasky/
├── dist/
│   └── Tasky.exe          # Your executable
├── build/                 # Temporary (can delete)
├── tasky.spec             # Build configuration
├── start_bot.py           # Source file
├── .env                   # Config (copy to dist/)
└── db.sqlite3             # Database (copy to dist/)
```

---

## Deployment

### For End Users:

1. **Download:**
   - Tasky.exe
   - .env (pre-configured or template)

2. **Setup:**
   - Install ngrok (one-time)
   - Edit .env with bot token
   - Run Tasky.exe

3. **Usage:**
   - Double-click Tasky.exe to start
   - Send /start to bot on Telegram
   - Press Ctrl+C to stop

### For Developers:

1. **Build:**
   ```bash
   pyinstaller tasky.spec
   ```

2. **Test:**
   ```bash
   cd dist
   Tasky.exe
   ```

3. **Distribute:**
   - Zip dist/ folder
   - Include README.txt
   - Include .env.example

---

## Summary

**What Changed:**
- ✅ `start_bot.py` - Detects if running as executable
- ✅ `Tasky/settings.py` - Loads .env from executable directory
- ✅ Database path - Uses executable directory
- ✅ Uvicorn - Runs programmatically in executable mode

**Benefits:**
- ✅ No Python installation required
- ✅ .env file next to executable
- ✅ Database next to executable
- ✅ Easy to distribute
- ✅ Works on any Windows machine

**Files to Distribute:**
- `Tasky.exe` - The bot executable
- `.env` - Configuration file
- `README.txt` - User instructions

---

## Next Steps

1. Build the executable: `pyinstaller tasky.spec`
2. Test in dist/ folder
3. Create distribution package
4. Share with users!

**🎉 Your bot is now ready to be distributed as a standalone executable!**

