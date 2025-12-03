# AI Video Generation Backend

Python Flask API server for the AI Video Generation Platform.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install flask flask-cors python-dotenv google-generativeai
```

Or install all requirements:
```bash
pip install -r ../requirements.txt
```

### 2. Configure API Keys

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GEMINI_API_KEY=your_actual_gemini_key_here
```

**Get Free Gemini API Key:**
- Visit: https://makersuite.google.com/app/apikey
- Sign in with Google
- Create API key (FREE!)

### 3. Start the Server

```bash
python api_server.py
```

The API will be available at: `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```http
GET /api/health
```

### Chat with AI Assistant
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Create a 30-second video about technology",
  "sessionId": "unique-session-id",
  "mode": "smart"
}
```

**Response:**
```json
{
  "response": "AI generated response...",
  "timestamp": "2025-11-30T12:00:00",
  "mode": "smart"
}
```

### Clear Chat History
```http
POST /api/chat/clear
Content-Type: application/json

{
  "sessionId": "unique-session-id"
}
```

### Get Chat History
```http
GET /api/chat/history?sessionId=unique-session-id
```

### Generate Video Script
```http
POST /api/generate/script
Content-Type: application/json

{
  "prompt": "Create a motivational video",
  "duration": 30,
  "style": "cinematic"
}
```

## 🔧 Backend Modules

- **`chatbot_engine.py`** - AI chat with Gemini/OpenAI/Claude support
- **`script_generator.py`** - Video script generation
- **`audio_generator.py`** - Text-to-speech audio generation
- **`pexels_video_generator.py`** - Stock video/image fetching
- **`image_to_video_animator.py`** - Image animation
- **`scene_builder.py`** - Scene composition
- **`config.py`** - Configuration and API keys

## 🔑 Required API Keys

### Essential (Free)
- **Google Gemini** - AI chat and script generation (FREE!)
  - Get: https://makersuite.google.com/app/apikey

### Optional
- **OpenAI** - Alternative AI provider (Paid)
- **Anthropic Claude** - Alternative AI provider (Paid)
- **Pexels** - Stock videos/images (FREE!)
- **Replicate** - AI video generation (Paid)
- **Stability AI** - Image generation (Paid)

## 🧪 Testing the API

### Using curl:
```bash
# Health check
curl http://localhost:5000/api/health

# Send chat message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello AI!", "sessionId": "test-123", "mode": "smart"}'
```

### Using Python:
```python
import requests

response = requests.post("http://localhost:5000/api/chat", json={
    "message": "Create a 30-second video about innovation",
    "sessionId": "test-session",
    "mode": "smart"
})

print(response.json())
```

## 🔗 Connecting Frontend

The React frontend automatically connects to `http://localhost:5000/api`.

Make sure:
1. Backend server is running on port 5000
2. Frontend is running on port 8080
3. CORS is enabled (handled by Flask-CORS)

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install flask flask-cors python-dotenv google-generativeai
```

### "API key not found" errors
- Check `.env` file exists in backend folder
- Verify `GEMINI_API_KEY` is set correctly
- Restart the server after updating `.env`

### CORS errors
- Flask-CORS is enabled by default
- Frontend should use `http://localhost:5000/api` (not localhost:3000)

### Port already in use
```bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <process_id> /F

# Or change port in api_server.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📦 Project Structure

```
backend/
├── api_server.py          # Flask API server
├── chatbot_engine.py      # AI chat logic
├── script_generator.py    # Script generation
├── audio_generator.py     # Audio generation
├── pexels_video_generator.py  # Stock media
├── config.py              # Configuration
├── .env                   # API keys (create this!)
├── .env.example           # Template
└── README.md             # This file
```

## 🚦 Development

### Run in development mode:
```bash
python api_server.py
```

### Run in production:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

## 📝 Notes

- The server uses Flask development server by default
- For production, use gunicorn or similar WSGI server
- Session data is stored in memory (resets on server restart)
- For persistent sessions, implement database storage
- AI responses are cached per session for better UX

## 🆘 Support

If you encounter issues:
1. Check that all dependencies are installed
2. Verify API keys are correct in `.env`
3. Ensure no other service is using port 5000
4. Check console for error messages
5. Review the Flask server logs

## 🔐 Security Notes

- Never commit `.env` file to git
- Keep API keys confidential
- Use environment variables in production
- Implement rate limiting for production use
- Add authentication for public deployment
