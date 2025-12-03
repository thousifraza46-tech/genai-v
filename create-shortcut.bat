@echo off
title Create Desktop Shortcut
color 0A

echo ========================================
echo   Creating Desktop Shortcut
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=AI Video Generator.lnk
set DESKTOP=%USERPROFILE%\Desktop

echo Creating shortcut on desktop...

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%DESKTOP%\%SHORTCUT_NAME%'); $Shortcut.TargetPath = '%SCRIPT_DIR%START.vbs'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.Description = 'AI Video Generator - Auto Start'; $Shortcut.IconLocation = 'shell32.dll,14'; $Shortcut.Save()"

echo.
echo ========================================
echo     SUCCESS!
echo ========================================
echo.
echo Desktop shortcut created:
echo %DESKTOP%\%SHORTCUT_NAME%
echo.
echo Double-click the shortcut to start the app!
echo.
pause
