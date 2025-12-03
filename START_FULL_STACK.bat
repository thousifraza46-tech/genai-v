@echo off
echo ========================================
echo   AI Video Generation Full Stack
echo   Starting Backend and Frontend
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js and try again
    pause
    exit /b 1
)

echo [1/3] Starting Backend Server (Flask on port 5000)...
echo.
start "AI Video Backend" cmd /k "cd backend && python api_server.py"

echo [2/3] Waiting for backend to initialize (5 seconds)...
timeout /t 5 /nobreak >nul

echo [3/3] Starting Frontend Server (Vite on port 8080)...
echo.
start "AI Video Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:8080
echo.
echo Press any key to open the app in your browser...
pause >nul

start http://localhost:8080

echo.
echo Servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
