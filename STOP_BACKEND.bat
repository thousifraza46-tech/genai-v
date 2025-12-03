@echo off
echo ============================================================
echo Stopping Backend Server
echo ============================================================
echo.

REM Find and kill Python processes on port 5000
echo [STOP] Finding backend server process...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    echo [STOP] Killing process ID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Also kill any Python processes running stable_server.py
wmic process where "commandline like '%%stable_server.py%%'" delete >nul 2>&1

echo [STOP] Backend server stopped
echo.
pause
