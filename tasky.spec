# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Tasky bot.
Build with: pyinstaller tasky.spec
"""

block_cipher = None

# Collect all Django files
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

django_datas = collect_data_files('django')
drf_datas = collect_data_files('rest_framework')

# Collect all hidden imports
hiddenimports = collect_submodules('django') + \
                collect_submodules('rest_framework') + \
                collect_submodules('telegram') + \
                collect_submodules('starlette') + \
                collect_submodules('uvicorn') + \
                [
                    'core_auth',
                    'core_auth.models',
                    'core_auth.admin',
                    'core_tasks',
                    'core_tasks.models',
                    'core_tasks.admin',
                    'core_tasks.tasks',
                    'core_bot',
                    'core_bot.bot',
                    'core_bot.utils',
                    'core_bot.handlers.basic',
                    'core_bot.handlers.projects',
                    'core_bot.handlers.tasks',
                    'core_bot.handlers.reports',
                    'core_bot.handlers.meetings',
                    'core_bot.handlers.approvals',
                    'core_bot.handlers.notifications',
                    'Tasky.settings',
                    'Tasky.asgi',
                    'Tasky.celery',
                ]

# Collect all data files
# NOTE: .env is NOT included - it should be placed next to the .exe
datas = [
    ('core_auth', 'core_auth'),
    ('core_tasks', 'core_tasks'),
    ('core_bot', 'core_bot'),
    ('Tasky', 'Tasky'),
    ('static', 'static'),  # Include static files (Django admin, etc.)
    # Don't include .env - users should provide their own
    # ('README.md', '.'),  # Optional
] + django_datas + drf_datas

a = Analysis(
    ['start_bot.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_asyncio.py'],  # Fix asyncio event loop issues
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
    icon=None,  # Add icon path if you have one
)

