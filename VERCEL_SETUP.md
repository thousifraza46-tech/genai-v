# Vercel Deployment Setup Guide

## Current Issue
Your frontend is deployed at `https://genaiv.vercel.app` but the backend is NOT deployed yet. The error shows:
- Frontend trying to connect to: `https://your-backend-domain.com/api`
- This is a placeholder that needs to be replaced

## Solution: Deploy Backend First

### Option 1: Deploy Backend to Railway (Recommended)

1. **Go to Railway**: https://railway.app
2. **Create New Project** → Deploy from GitHub
3. **Select Repository**: `thousifraza46-tech/genai-v`
4. **Select Root Directory**: Choose `backend` folder
5. **Add Environment Variables**:
   ```
   PORT=5000
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://genaiv.vercel.app
   PEXELS_API_KEY=your_pexels_key
   GEMINI_API_KEY=your_gemini_key
   DEEPAI_API_KEY=your_deepai_key
   ```
6. **Deploy** and get your Railway URL (e.g., `https://genai-backend-production.up.railway.app`)

### Option 2: Deploy Backend to Render

1. **Go to Render**: https://render.com
2. **New Web Service** → Connect GitHub repo `genai-v`
3. **Configure**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python start_server.py`
4. **Add Environment Variables** (same as Railway above)
5. **Deploy** and get your Render URL (e.g., `https://genai-backend.onrender.com`)

## Update Vercel Environment Variables

Once backend is deployed:

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard
2. **Select Project**: `genaiv`
3. **Settings** → **Environment Variables**
4. **Add Variables**:
   - `VITE_API_URL` = `https://your-railway-or-render-url.com/api`
   - `VITE_ASSETS_URL` = `https://your-railway-or-render-url.com/assets`
5. **Redeploy** your frontend

## Quick Fix for Testing (Local Backend)

If you want to test with local backend temporarily:

1. **Run Backend Locally**: `cd backend; python api_server.py`
2. **Use Ngrok** to expose local backend:
   ```powershell
   ngrok http 5000
   ```
3. **Update Vercel Env Variables** with ngrok URL
4. **Redeploy Frontend**

## Important Notes

- ✅ Frontend is already deployed: `https://genaiv.vercel.app`
- ❌ Backend is NOT deployed (still shows placeholder URL)
- ⚠️ CORS is properly configured in backend to accept requests from your Vercel frontend
- ⚠️ You MUST deploy backend first before the frontend will work

## Current Backend Status

Your backend is running locally on `localhost:5000` but is NOT accessible from the internet. The deployed Vercel frontend cannot reach it.

**Next Step**: Choose Railway or Render and deploy the backend, then update Vercel environment variables with the actual backend URL.
