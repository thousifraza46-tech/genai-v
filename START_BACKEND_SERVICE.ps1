# PowerShell script to start backend as background service
# This runs independently of PowerShell/CMD windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Backend as Background Service" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing backend servers
Write-Host "[CLEANUP] Stopping existing servers..." -ForegroundColor Yellow
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess | 
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 2

# Check Waitress installation
Write-Host "[CHECK] Verifying dependencies..." -ForegroundColor Yellow
$waitressCheck = python -c "import waitress; print('OK')" 2>$null
if (-not $waitressCheck) {
    Write-Host "[INSTALL] Installing Waitress..." -ForegroundColor Yellow
    pip install waitress --quiet
}

# Start server as background process (independent of this PowerShell session)
Write-Host "[START] Launching backend server..." -ForegroundColor Green
$pythonPath = (Get-Command python).Source
$serverScript = "C:\Gen\backend\stable_server.py"

# Create a startup script that runs independently
$startupScript = @"
Set-Location 'C:\Gen\backend'
Start-Process -FilePath '$pythonPath' -ArgumentList '$serverScript' -WindowStyle Hidden -PassThru
"@

# Run in a new detached process
Start-Process powershell -ArgumentList "-NoProfile -Command `"$startupScript`"" -WindowStyle Hidden

Start-Sleep -Seconds 3

# Verify server started
Write-Host "[VERIFY] Checking server status..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Backend Running" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "URL: http://localhost:5000" -ForegroundColor White
    Write-Host "Status: $($response.status)" -ForegroundColor Green
    Write-Host ""
    Write-Host "The server is now running in the background." -ForegroundColor Cyan
    Write-Host "You can close this window safely." -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop: Run STOP_BACKEND.bat" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "[ERROR] Server did not start properly" -ForegroundColor Red
    Write-Host "Check for port conflicts or run START_BACKEND.bat to see errors" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to close this window"
