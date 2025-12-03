# PowerShell Script to Run Backend Server
# This keeps the server running stably without crashes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Backend Server Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location "C:\Gen\backend"

# Check if Waitress is installed
Write-Host "[CHECK] Checking Waitress installation..." -ForegroundColor Yellow
$waitressCheck = python -c "import waitress; print('OK')" 2>$null
if (-not $waitressCheck) {
    Write-Host "[INSTALL] Installing Waitress for stable server..." -ForegroundColor Yellow
    pip install waitress --quiet
    Write-Host "[INSTALL] Waitress installed!" -ForegroundColor Green
}

# Kill existing servers on port 5000
Write-Host "[CLEANUP] Stopping any existing servers..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($processes) {
    foreach ($pid in $processes) {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[CLEANUP] Port 5000 cleared" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   SERVER STARTING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "URL: http://localhost:5000" -ForegroundColor White
Write-Host "API: http://localhost:5000/api" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Run the server
python stable_server.py
