@echo off
color 0A
title Backend Server Manager

:MENU
cls
echo.
echo ========================================
echo    BACKEND SERVER MANAGER
echo ========================================
echo.
echo  1. Start Backend (Background Mode)
echo  2. Start Backend (Visible Window)
echo  3. Stop Backend
echo  4. Check Server Status
echo  5. Exit
echo.
echo ========================================
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto START_HIDDEN
if "%choice%"=="2" goto START_VISIBLE
if "%choice%"=="3" goto STOP
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto EXIT
goto MENU

:START_HIDDEN
cls
echo.
echo [INFO] Starting backend in background mode...
echo [INFO] Server will run invisibly
echo.
python run_backend.py
pause
goto MENU

:START_VISIBLE
cls
echo.
echo [INFO] Starting backend with visible window...
echo [WARN] Keep the window open while using the app
echo.
start "Backend Server" cmd /k "cd /d %~dp0backend && python stable_server.py"
timeout /t 3 >nul
goto MENU

:STOP
cls
echo.
echo [INFO] Stopping backend server...
echo.
call STOP_BACKEND.bat
goto MENU

:STATUS
cls
echo.
call CHECK_BACKEND_STATUS.bat
goto MENU

:EXIT
exit
