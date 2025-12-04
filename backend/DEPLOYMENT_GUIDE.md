# Backend Deployment Guide

## ✅ Optimized for Railway/Render (< 1 GB Docker Image)

This backend has been optimized to deploy successfully within the 4 GB image size limit.

### 📦 What's Included

**Core Features (Enabled in Production):**
- ✅ Flask API server
- ✅ Google Gemini AI chatbot
- ✅ Edge TTS audio generation
- ✅ Pexels image/video search
- ✅ Script generation
- ✅ Scene building

**Optional Features (Disabled by Default):**
- ⚠️ NLTK (keyword extraction) - Falls back to simple extraction
- ⚠️ MoviePy (video editing) - Requires local development
- ⚠️ Combine Clips feature - Requires MoviePy
- ⚠️ Export Video feature - Requires MoviePy

---

## 🚀 Deploy to Railway

### Prerequisites
- Git repository pushed to GitHub
- Railway account (free tier available)
- API keys for services you want to use

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Navigate to Backend
```bash
cd backend
```

### Step 3: Login to Railway
```bash
railway login
```

### Step 4: Initialize Project
```bash
railway init
# Select "Create new project"
# Give it a name like "genai-backend"
```

### Step 5: Set Environment Variables
```bash
railway variables --set PORT=5000
railway variables --set ENVIRONMENT=production
railway variables --set ALLOWED_ORIGINS=https://genaiv-three.vercel.app,https://genaiv.vercel.app

# Optional API keys (only if you have them)
railway variables --set GEMINI_API_KEY=your_key_here
railway variables --set PEXELS_API_KEY=your_key_here
```

### Step 6: Deploy
```bash
railway up
```

### Step 7: Get Your URL
```bash
railway domain
# Copy the URL shown (e.g., genai-backend.railway.app)
```

### Step 8: Update Frontend
Go to Vercel dashboard → Your project → Settings → Environment Variables:
- Add: `VITE_API_URL` = `https://your-railway-url.railway.app`
- Redeploy frontend

---

## 🎨 Deploy to Render

### Step 1: Connect Repository
1. Go to https://render.com/dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select `backend` directory

### Step 2: Configure Service
- **Name:** genai-backend
- **Environment:** Docker
- **Dockerfile Path:** backend/Dockerfile
- **Plan:** Free (or Starter for better performance)

### Step 3: Environment Variables
Add these in Render dashboard:
```
PORT=5000
ENVIRONMENT=production
ALLOWED_ORIGINS=https://genaiv-three.vercel.app,https://genaiv.vercel.app
GEMINI_API_KEY=your_key_here
PEXELS_API_KEY=your_key_here
```

### Step 4: Deploy
- Click "Create Web Service"
- Wait 5-10 minutes for build
- Copy the URL (e.g., genai-backend.onrender.com)

### Step 5: Update Frontend
Update Vercel environment variable:
- `VITE_API_URL` = `https://your-render-url.onrender.com`

---

## 🔧 Dockerfile Details

The included `Dockerfile` creates an optimized image:

```dockerfile
FROM python:3.11-slim          # Lightweight base image
WORKDIR /app
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "start_server.py"]
```

**Image Size:** ~800 MB (well under 4 GB limit)

---

## 📋 Requirements.txt Structure

The `requirements.txt` is organized by priority:

**Core (Always Installed):**
```
flask==3.0.0
flask-cors==4.0.0
requests==2.31.0
python-dotenv==1.0.0
waitress==2.1.2
```

**Optional AI Features (Commented out by default):**
```
google-generativeai==0.3.2    # Gemini AI chatbot
edge-tts==6.1.9               # Audio generation
```

**Heavy Features (Commented out - for local dev only):**
```
# nltk==3.8.1                 # Keyword extraction
# moviepy==1.0.3              # Video editing
# imageio==2.31.3
# imageio-ffmpeg==0.4.9
# pillow==10.0.0
# numpy==1.24.3
```

---

## 🧪 Test Deployment

After deployment, test these endpoints:

### Health Check
```bash
curl https://your-url.railway.app/api/health
```
Expected: `{"status": "healthy", "environment": "production"}`

### Chat Endpoint
```bash
curl -X POST https://your-url.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, can you help me?"}'
```

### Script Generation
```bash
curl -X POST https://your-url.railway.app/api/generate-script \
  -H "Content-Type: application/json" \
  -d '{"prompt": "sunset beach", "duration": "15 seconds"}'
```

---

## ⚡ Enable Heavy Features (Local Development)

To enable video editing features locally:

1. Uncomment packages in `requirements.txt`:
```
moviepy==1.0.3
imageio==2.31.3
imageio-ffmpeg==0.4.9
pillow==10.0.0
numpy==1.24.3
nltk==3.8.1
```

2. Install locally:
```bash
pip install -r requirements.txt
```

3. **Don't push to production** - these add 7+ GB to image size

---

## 🐛 Troubleshooting

### "Image size exceeded limit"
- Check that heavy packages (moviepy, nltk) are commented out in requirements.txt
- Verify Dockerfile uses `python:3.11-slim` (not full Python image)

### "Module not found" errors
- Check which features you're using
- Uncomment needed packages in requirements.txt
- Re-deploy

### Build fails on Railway/Render
- Check logs: `railway logs` or Render dashboard
- Verify Dockerfile exists in backend/
- Ensure all files are committed to Git

### CORS errors on frontend
- Check `ALLOWED_ORIGINS` environment variable includes your Vercel URL
- Ensure frontend `VITE_API_URL` points to correct backend URL

---

## 📊 Feature Availability

| Feature | Local Dev | Production |
|---------|-----------|------------|
| AI Chat | ✅ | ✅ |
| Script Generation | ✅ | ✅ |
| Audio Generation | ✅ | ✅ |
| Image Search | ✅ | ✅ |
| Scene Building | ✅ | ✅ |
| **Export Video** | ✅ | ❌ * |
| **Combine Clips** | ✅ | ❌ * |
| Keyword Extraction | ✅ (NLTK) | ✅ (Simple) |

\* *Requires MoviePy - disabled in production to reduce image size*

---

## 💡 Alternative: Split Services

For full feature parity in production, consider:

1. **API Service** (Railway/Render) - Chat, scripts, search
2. **Video Processing Service** (AWS Lambda/GCP Cloud Functions) - Export, combine
3. **Cloud Storage** (S3/GCS) - Store video assets

This keeps the main API lightweight while enabling heavy video processing.

---

## 📝 Summary

✅ **Current state:** Lightweight deployment (< 1 GB) with core features  
✅ **What works:** Chat, script generation, audio, image search  
⚠️ **What's disabled:** Video editing (Export, Combine Clips)  
🔧 **Next steps:** Deploy using Railway or Render, update frontend URL
