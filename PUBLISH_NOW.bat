@echo off
title NEXUS 1-Click Automated Publisher
echo ========================================================
echo        NEXUS 1-Click GitHub and Website Publisher
echo ========================================================
cd /d "E:\NEXUS"
"E:\NEXUS\.venv\Scripts\python.exe" "E:\NEXUS\auto_publish.py"
pause
