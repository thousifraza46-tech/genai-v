# Quick Setup Guide for Deployment Issue Fix

## Problem
Frontend is deployed on Vercel but backend is not deployed, causing 404 errors.

## Solution (5 Minutes)

### 1. Deploy Backend to Railway

Run this command in PowerShell:
```powershell
.\deploy-backend-railway.ps1
```

OR manually:
```powershell
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway init
railway up
```

### 2. Configure Railway Environment Variables

Go to: https://railway.app/dashboard → Your Project → Variables

Add these:
```
PORT=5000
ENVIRONMENT=production
ALLOWED_ORIGINS=https://genai-studio-steel.vercel.app
GROQ_API_KEY=your_actual_key
GEMINI_API_KEY=your_actual_key
PEXELS_API_KEY=your_actual_key
HUGGINGFACE_API_KEY=your_actual_key
DEEPAI_API_KEY=your_actual_key
ELEVEN_LABS_API_KEY=your_actual_key
```

### 3. Update Vercel Environment Variables

Go to: https://vercel.com/dashboard → Your Project → Settings → Environment Variables

Add these (replace with your actual Railway URL):
```
VITE_API_URL=https://your-project.railway.app/api
VITE_ASSETS_URL=https://your-project.railway.app/assets
```

### 4. Redeploy Frontend

In Vercel dashboard:
- Go to Deployments tab
- Click the three dots on latest deployment
- Click "Redeploy"

## Done!

Your app should now work. The frontend will connect to the Railway backend.

## Verify

1. Check backend: `https://your-project.railway.app/api/health`
2. Check frontend: `https://genai-studio-steel.vercel.app`
3. Connection indicator should show "Connected"
