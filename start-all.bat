@echo off
title AI Video Generator - Auto Startup
color 0B

echo ========================================
echo    AI Video Generator - Auto Startup
echo ========================================
echo.

REM Kill existing processes
echo Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo    Backend port 5000 cleared
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo    Frontend port 8080 cleared
)

timeout /t 1 >nul

REM Start Backend
echo.
echo Starting Backend Server...
cd /d "%~dp0backend"
start "Backend Server" /MIN python api_server.py
echo    Backend started on http://localhost:5000

REM Wait for backend
timeout /t 3 >nul

REM Start Frontend
echo.
echo Starting Frontend Server...
cd /d "%~dp0"
start "Frontend Server" /MIN npm run dev
echo    Frontend started on http://localhost:8080

REM Wait for frontend
timeout /t 5 >nul

echo.
echo ========================================
echo          ALL SERVICES RUNNING
echo ========================================
echo.
echo Frontend:  http://localhost:8080
echo Backend:   http://localhost:5000
echo API Keys:  Connected directly from backend
echo.
echo Open your browser to http://localhost:8080
echo.
echo Press any key to open browser and keep services running...
pause >nul

start http://localhost:8080

echo.
echo Services are running in background windows.
echo Close those windows to stop the services.
echo.
pause
