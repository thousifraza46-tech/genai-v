# Auto-start script for both Frontend and Backend
# No manual terminal commands needed

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Video Generator - Auto Startup   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing processes on ports 5000 and 8080
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow

# Kill backend (port 5000)
$backend = Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
if ($backend) {
    $backendPid = $backend.OwningProcess
    Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Stopped existing backend (PID: $backendPid)" -ForegroundColor Green
}

# Kill frontend (port 8080)
$frontend = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($frontend) {
    $frontendPid = $frontend.OwningProcess
    Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
    Write-Host "   ✓ Stopped existing frontend (PID: $frontendPid)" -ForegroundColor Green
}

Start-Sleep -Seconds 1

# Start Backend Server (Minimized)
Write-Host ""
Write-Host "🚀 Starting Backend Server..." -ForegroundColor Cyan
$backendPath = Join-Path $PSScriptRoot "backend\api_server.py"
$backendProcess = Start-Process python -ArgumentList $backendPath -WindowStyle Hidden -PassThru
Write-Host "   ✓ Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
Write-Host "   📡 Backend running on http://localhost:5000" -ForegroundColor White

# Wait for backend to initialize
Write-Host ""
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Test backend connection
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -Method GET -TimeoutSec 5
    Write-Host "   ✓ Backend health check passed" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Backend may still be initializing..." -ForegroundColor Yellow
}

# Start Frontend Server (Minimized)
Write-Host ""
Write-Host "🚀 Starting Frontend Server..." -ForegroundColor Cyan
$frontendProcess = Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
Write-Host "   ✓ Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
Write-Host "   🌐 Frontend running on http://localhost:8080" -ForegroundColor White

# Wait for frontend to initialize
Write-Host ""
Write-Host "⏳ Waiting for frontend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "         🎉 ALL SERVICES RUNNING        " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Frontend:  http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔧 Backend:   http://localhost:5000" -ForegroundColor Cyan
Write-Host "🔑 API Keys:  Connected directly from backend" -ForegroundColor Cyan
Write-Host ""
Write-Host "✨ Open your browser to http://localhost:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor White
Write-Host ""

# Keep script running and monitor services
try {
    while ($true) {
        Start-Sleep -Seconds 10
        
        # Check if processes are still running
        $backendRunning = Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
        $frontendRunning = Get-Process -Id $frontendProcess.Id -ErrorAction SilentlyContinue
        
        if (-not $backendRunning) {
            Write-Host "⚠ Backend stopped unexpectedly! Restarting..." -ForegroundColor Red
            $backendProcess = Start-Process python -ArgumentList $backendPath -WindowStyle Hidden -PassThru
            Write-Host "✓ Backend restarted (PID: $($backendProcess.Id))" -ForegroundColor Green
        }
        
        if (-not $frontendRunning) {
            Write-Host "⚠ Frontend stopped unexpectedly! Restarting..." -ForegroundColor Red
            $frontendProcess = Start-Process npm -ArgumentList "run", "dev" -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -PassThru
            Write-Host "✓ Frontend restarted (PID: $($frontendProcess.Id))" -ForegroundColor Green
        }
    }
} finally {
    # Cleanup on exit
    Write-Host ""
    Write-Host "🛑 Stopping all services..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "✓ All services stopped" -ForegroundColor Green
}
