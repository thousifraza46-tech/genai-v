# 🔗 Backend-Frontend Architecture Map

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         🎨 FRONTEND (React + TypeScript)                │
│                         http://localhost:8080                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP Requests
                                    │ (fetch API)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    🌐 API SERVER (Flask + CORS)                         │
│                    http://localhost:5000/api                            │
│                                                                           │
│  📡 Endpoints:                                                           │
│  ├─ GET  /api/health              → Health check                        │
│  ├─ POST /api/chat                → AI chat assistance                  │
│  ├─ POST /api/generate/script     → Script generation                   │
│  ├─ POST /api/generate/audio      → Audio generation                    │
│  ├─ POST /api/generate/images     → Image fetching                      │
│  └─ POST /api/generate/render     → Video rendering                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
    ┏━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━┓
    ┃  🤖 CHATBOT   ┃  ┃  📝 SCRIPT     ┃  ┃  🔊 AUDIO      ┃
    ┃    ENGINE      ┃  ┃  GENERATOR     ┃  ┃  GENERATOR     ┃
    ┗━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━┛
    chatbot_engine.py   script_generator.py   audio_generator.py
                  │                 │                 │
                  ▼                 ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
    │ Gemini AI        │  │ Gemini AI        │  │ Microsoft Edge   │
    │ OpenAI GPT       │  │ (gemini-1.5-     │  │ TTS              │
    │ Anthropic Claude │  │  flash)          │  │ (6 voices)       │
    └──────────────────┘  └──────────────────┘  └──────────────────┘
                  
                  
                  ▼                 ▼
    ┏━━━━━━━━━━━━━━━━┓  ┏━━━━━━━━━━━━━━━━┓
    ┃  🖼️ IMAGE      ┃  ┃  🎬 SCENE      ┃
    ┃  GENERATOR     ┃  ┃  BUILDER       ┃
    ┗━━━━━━━━━━━━━━━━┛  ┗━━━━━━━━━━━━━━━━┛
    pexels_video_       scene_builder.py
    generator.py              │
         │                    │
         ▼                    ▼
    ┌──────────────────┐  ┌──────────────────┐
    │ Pexels API       │  │ MoviePy          │
    │ (Stock Images    │  │ FFmpeg           │
    │  & Videos)       │  │ (Video           │
    └──────────────────┘  │  Processing)     │
                          └──────────────────┘
```

---

## 🔄 Data Flow - Generate Video Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER ENTERS PROMPT                              │
│              "Ocean sunset with waves crashing"                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│   STAGE 1: SCRIPT GENERATION (5-10s)                                │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                       │
│   Frontend → POST /api/generate/script                              │
│              { prompt: "Ocean sunset...", duration: 30 }            │
│              │                                                       │
│              ▼                                                       │
│   Backend  → ScriptGenerator().generate_script()                    │
│              │                                                       │
│              ▼                                                       │
│   Gemini AI → Generates professional narration script               │
│              │                                                       │
│              ▼                                                       │
│   Response ← { script: "...", word_count: 120,                      │
│                estimated_duration: 30, source: "gemini-ai" }        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│   STAGE 2: AUDIO GENERATION (5-10s)                                 │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                       │
│   Frontend → POST /api/generate/audio                               │
│              { script: "...", voice: "en-US-ChristopherNeural" }    │
│              │                                                       │
│              ▼                                                       │
│   Backend  → AudioGenerator().generate_audio()                      │
│              │                                                       │
│              ▼                                                       │
│   Edge TTS → Generates MP3 audio file                               │
│              │                                                       │
│              ▼                                                       │
│   Saves to → assets/audio/narration_1234567890.mp3                  │
│              │                                                       │
│              ▼                                                       │
│   Response ← { audio_url: "/assets/audio/...",                      │
│                duration: 28.5, voice: "Christopher" }               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│   STAGE 3: IMAGE GENERATION (5-10s)                                 │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                       │
│   Frontend → POST /api/generate/images                              │
│              { prompt: "Ocean sunset...", count: 3 }                │
│              │                                                       │
│              ▼                                                       │
│   Backend  → PexelsVideoGenerator().search_images()                 │
│              │                                                       │
│              ▼                                                       │
│   NLTK     → Extracts keywords: "ocean sunset waves"                │
│              │                                                       │
│              ▼                                                       │
│   Pexels   → Searches stock images with keywords                    │
│              │                                                       │
│              ▼                                                       │
│   Response ← { images: [                                            │
│                  { id: 1, url: "https://...", scene: 1 },           │
│                  { id: 2, url: "https://...", scene: 2 },           │
│                  { id: 3, url: "https://...", scene: 3 }            │
│                ], count: 3 }                                         │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│   STAGE 4: VIDEO RENDERING (15-30s) ⚠️ NEEDS COMPLETION             │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━    │
│                                                                       │
│   Frontend → POST /api/generate/render                              │
│              { script: "...", audio_path: "...",                    │
│                image_urls: [...], duration: 30 }                    │
│              │                                                       │
│              ▼                                                       │
│   Backend  → scene_builder.combine_videos()  [PLACEHOLDER]          │
│              │                                                       │
│              ▼                                                       │
│   TODO:                                                              │
│   1. Download images from URLs                                      │
│   2. Create video clips from images (MoviePy)                       │
│   3. Add audio narration overlay                                    │
│   4. Combine all clips into final video                             │
│   5. Save to assets/videos/video_1234567890.mp4                     │
│              │                                                       │
│              ▼                                                       │
│   Response ← { video_url: "/assets/videos/...",                     │
│                duration: 30, status: "completed" }                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ✅ VIDEO COMPLETE!
                   Display in frontend player
```

---

## 📦 Module Dependencies

```
chatbot_engine.py
├── google.generativeai (Gemini AI)
├── openai (OpenAI GPT) [optional]
├── anthropic (Claude) [optional]
└── dotenv (environment variables)

script_generator.py
├── google.generativeai (Gemini AI)
├── config (local config)
└── fallback generation (no dependencies)

audio_generator.py
├── edge_tts (Microsoft TTS)
├── asyncio (async processing)
└── os, time, random

pexels_video_generator.py
├── requests (HTTP calls)
├── nltk (keyword extraction)
├── intelligent_trainer [optional]
├── smart_learner [optional]
└── os, json, logging

scene_builder.py
├── moviepy (video processing)
├── requests (download files)
├── urllib (URL handling)
└── concurrent.futures (parallel downloads)

api_server.py
├── flask (web framework)
├── flask_cors (CORS support)
└── all backend modules above
```

---

## 🔐 API Keys Flow

```
┌────────────────┐
│  .env file     │
│  (backend/)    │
└────────────────┘
        │
        ├─→ GEMINI_API_KEY      → chatbot_engine.py
        │                        → script_generator.py
        │
        ├─→ PEXELS_API_KEY      → pexels_video_generator.py
        │
        ├─→ OPENAI_API_KEY      → chatbot_engine.py [optional]
        │
        └─→ ANTHROPIC_API_KEY   → chatbot_engine.py [optional]
```

---

## 🎯 Connection Status Matrix

| Frontend Tab | Backend Module | Status | API Endpoint |
|--------------|----------------|--------|--------------|
| AI Assistance | chatbot_engine.py | ✅ Connected | POST /api/chat |
| Generate Video (Stage 1) | script_generator.py | ✅ Connected | POST /api/generate/script |
| Generate Video (Stage 2) | audio_generator.py | ✅ Connected | POST /api/generate/audio |
| Generate Video (Stage 3) | pexels_video_generator.py | ✅ Connected | POST /api/generate/images |
| Generate Video (Stage 4) | scene_builder.py | ⚠️ Partial | POST /api/generate/render |

**Legend:**
- ✅ Fully connected and tested
- ⚠️ Endpoint exists but needs full implementation
- ❌ Not connected

---

## 📊 Performance Metrics

**Estimated Processing Times:**

| Stage | With API Keys | Without API Keys | Notes |
|-------|--------------|------------------|-------|
| Script Generation | 2-5 seconds | 1 second | Gemini AI vs Fallback |
| Audio Generation | 3-8 seconds | N/A | Edge TTS required |
| Image Search | 2-5 seconds | N/A | Pexels API required |
| Video Rendering | 15-45 seconds | N/A | Depends on video length |

**Total Pipeline Time:** ~25-60 seconds for 30-second video

---

**Last Updated:** 2025-11-30  
**All Core Connections:** ✅ Working  
**Next Task:** Complete video rendering integration
