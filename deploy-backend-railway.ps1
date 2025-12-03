# Railway Backend Deployment Script
# This script helps you deploy the Python backend to Railway

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "   Backend Deployment to Railway" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Check if Railway CLI is installed
Write-Host "Step 1: Checking Railway CLI..." -ForegroundColor Yellow
$railwayInstalled = Get-Command railway -ErrorAction SilentlyContinue

if (-not $railwayInstalled) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Red
    npm install -g @railway/cli
    Write-Host "✅ Railway CLI installed!`n" -ForegroundColor Green
} else {
    Write-Host "✅ Railway CLI already installed`n" -ForegroundColor Green
}

# Step 2: Login to Railway
Write-Host "Step 2: Login to Railway..." -ForegroundColor Yellow
Write-Host "Opening browser for authentication...`n" -ForegroundColor Cyan
railway login

# Step 3: Initialize Railway project
Write-Host "`nStep 3: Creating Railway project..." -ForegroundColor Yellow
Set-Location backend
railway init

# Step 4: Deploy
Write-Host "`nStep 4: Deploying backend to Railway..." -ForegroundColor Yellow
Write-Host "This may take a few minutes...`n" -ForegroundColor Cyan
railway up

# Step 5: Get the deployment URL
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "   Deployment Complete!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Copy your Railway backend URL from the output above" -ForegroundColor White
Write-Host "2. Go to Railway dashboard: https://railway.app/dashboard" -ForegroundColor White
Write-Host "3. Click on your project → Variables tab" -ForegroundColor White
Write-Host "4. Add these environment variables:`n" -ForegroundColor White

Write-Host "   PORT=5000" -ForegroundColor Cyan
Write-Host "   ENVIRONMENT=production" -ForegroundColor Cyan
Write-Host "   ALLOWED_ORIGINS=https://genai-studio-steel.vercel.app" -ForegroundColor Cyan
Write-Host "   GROQ_API_KEY=your_groq_key" -ForegroundColor Cyan
Write-Host "   GEMINI_API_KEY=your_gemini_key" -ForegroundColor Cyan
Write-Host "   PEXELS_API_KEY=your_pexels_key" -ForegroundColor Cyan
Write-Host "   HUGGINGFACE_API_KEY=your_huggingface_key" -ForegroundColor Cyan
Write-Host "   DEEPAI_API_KEY=your_deepai_key" -ForegroundColor Cyan
Write-Host "   ELEVEN_LABS_API_KEY=your_elevenlabs_key`n" -ForegroundColor Cyan

Write-Host "5. Go to Vercel dashboard: https://vercel.com/dashboard" -ForegroundColor White
Write-Host "6. Select your project → Settings → Environment Variables" -ForegroundColor White
Write-Host "7. Add:`n" -ForegroundColor White

Write-Host "   VITE_API_URL=https://your-railway-url.railway.app/api" -ForegroundColor Cyan
Write-Host "   VITE_ASSETS_URL=https://your-railway-url.railway.app/assets`n" -ForegroundColor Cyan

Write-Host "8. Redeploy frontend in Vercel (Deployments → Redeploy)`n" -ForegroundColor White

Write-Host "========================================`n" -ForegroundColor Green

Set-Location ..
