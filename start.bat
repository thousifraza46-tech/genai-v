@echo off
echo ========================================
echo AI Video Generation Platform
echo Starting Backend and Frontend Servers
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from nodejs.org
    pause
    exit /b 1
)

echo [1/4] Checking Python dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask backend dependencies...
    pip install flask flask-cors python-dotenv google-generativeai
)

echo [2/4] Checking .env file...
if not exist "backend\.env" (
    echo [WARNING] backend\.env not found!
    echo Creating from template...
    copy "backend\.env.example" "backend\.env"
    echo.
    echo Please edit backend\.env and add your API keys:
    echo   - GEMINI_API_KEY (get free at: https://makersuite.google.com/app/apikey)
    echo.
    pause
)

echo [3/4] Starting Flask Backend Server...
start "AI Backend - Flask" cmd /k "cd backend && python api_server.py"
timeout /t 3 /nobreak >nul

echo [4/4] Starting React Frontend...
start "AI Frontend - React" cmd /k "npm run dev"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Servers Starting...
echo ========================================
echo Backend API:  http://localhost:5000
echo Frontend App: http://localhost:8080
echo.
echo Press any key to open the app in your browser...
pause >nul

start http://localhost:8080

echo.
echo Servers are running!
echo Close the terminal windows to stop the servers.
echo.
pause
