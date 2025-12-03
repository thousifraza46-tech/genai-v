@echo off
echo ============================================================
echo Backend Server Status Check
echo ============================================================
echo.

REM Check if port 5000 is listening
netstat -ano | findstr :5000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo [STATUS] Backend server is RUNNING
    echo [URL] http://localhost:5000
    echo.
    
    REM Show the process details
    echo [PROCESS INFO]
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
        tasklist /FI "PID eq %%a" /FO TABLE
    )
) else (
    echo [STATUS] Backend server is NOT running
    echo.
    echo [ACTION] Run START_BACKEND_HIDDEN.vbs to start it
)

echo.
pause
