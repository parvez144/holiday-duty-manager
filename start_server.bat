@echo off
TITLE Holiday Duty Manager Server
echo Starting Holiday Duty Manager...
cd /d "%~dp0"
echo Starting Attendance Sync...
start "Attendance Sync" venv\Scripts\python sync_data.py --loop

echo Starting Web Server...
venv\Scripts\python serve.py
pause
