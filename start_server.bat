@echo off
TITLE Holiday Duty Manager Server
echo Starting Holiday Duty Manager...
cd /d "%~dp0"
call venv\Scripts\activate
python serve.py
pause
