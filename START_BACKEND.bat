@echo off
echo ============================================================
echo Starting Ultra-Stable Backend Server
echo ============================================================
echo.

cd /d "%~dp0backend"

REM Check and install Waitress if needed
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo [SETUP] Installing Waitress for production stability...
    pip install waitress --quiet
    echo [SETUP] Waitress installed successfully
    echo.
)

REM Kill any existing Python servers on port 5000
echo [CLEANUP] Checking for existing servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do taskkill /F /PID %%a >nul 2>&1
echo [CLEANUP] Port 5000 cleared
echo.

REM Start the stable server
echo [START] Launching backend server...
echo [START] URL: http://localhost:5000
echo [START] Keep this window open while using the app
echo.
echo ============================================================
echo SERVER RUNNING - DO NOT CLOSE THIS WINDOW
echo ============================================================
echo.

python stable_server.py

echo.
echo [STOPPED] Server has stopped
pause
