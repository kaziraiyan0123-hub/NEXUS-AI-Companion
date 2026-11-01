# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

added_files = [
    ('nexus_icon.ico', '.'),
    ('nexus_icon.png', '.'),
]

a = Analysis(
    ['main.py'],
    pathex=['E:\\NEXUS'],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'pypdf',
        'openpyxl',
        'psutil',
        'speech_recognition',
        'pygame',
        'edge_tts',
        'PySide6.QtPdf',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'sqlite3',
        'win32com.client',
        'markdown',
        'pygments',
        'pygments.lexers',
        'pygments.formatters',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
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
    name='NEXUS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='nexus_icon.ico'
)
