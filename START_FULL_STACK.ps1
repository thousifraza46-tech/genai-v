#!/usr/bin/env pwsh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI Video Generation Full Stack" -ForegroundColor Cyan
Write-Host "  Starting Backend and Frontend" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Starting Backend Server (Flask on port 5000)..." -ForegroundColor Green
Write-Host ""

# Start backend in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python api_server.py"

Write-Host "[2/3] Waiting for backend to initialize (5 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "[3/3] Starting Frontend Server (Vite on port 8080)..." -ForegroundColor Green
Write-Host ""

# Start frontend in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Both servers are starting!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  " -NoNewline
Write-Host "http://localhost:5000" -ForegroundColor Blue
Write-Host "Frontend: " -NoNewline
Write-Host "http://localhost:8080" -ForegroundColor Blue
Write-Host ""
Write-Host "Waiting 5 more seconds before opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Open browser
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "✓ Servers are running in separate windows." -ForegroundColor Green
Write-Host "✓ Browser opened to http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "Close the PowerShell windows to stop the servers." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit this window (servers will continue running)"
