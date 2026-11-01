@echo off
title NEXUS AI Desktop Companion
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" launch.py
) else (
    start "" python launch.py
)
exit
