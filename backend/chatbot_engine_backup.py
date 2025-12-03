# -*- coding: utf-8 -*-
"""
AI Chatbot Engine for Video Generation Assistant
Provides intelligent responses using NLP and Gen AI
"""
import random
import os
from datetime import datetime
import google.generativeai as genai

class ChatbotEngine:
    def __init__(self):
        self.conversations = {}
        
        # Initialize Gemini AI
        try:
            from config import GEMINI_API_KEY
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_ai = True
            print("[Chatbot] ✅ Gemini AI initialized successfully")
        except Exception as e:
            print(f"[Chatbot] ⚠️ AI initialization failed: {e}, using fallback responses")
            self.use_ai = False
        
        # System prompt for AI context
        self.system_context = """You are an expert AI assistant for a video generation platform. Your role is to help users create professional videos by:

1. **Script Writing**: Guide users in creating engaging video scripts with proper structure
2. **Visual Selection**: Advise on finding and selecting the right images/videos
3. **Video Editing**: Provide tips on trimming, effects, transitions, and composition
4. **Creative Ideas**: Suggest unique video concepts and trending topics
5. **Platform Optimization**: Share best practices for different social media platforms

Key capabilities of the platform:
- Generate video scripts from text prompts
- Search and fetch images/videos from Pexels API
- Create AI voiceovers from scripts
- Edit videos with timeline, trim, speed, volume controls
- Apply visual effects (brightness, contrast, rotation, flip)
- Export final videos in MP4 format

Communication style:
- Be friendly, encouraging, and professional
- Provide actionable, step-by-step guidance
- Use emojis appropriately for visual appeal
- Keep responses concise but informative (3-5 paragraphs max)
- Ask clarifying questions when needed
- Reference specific platform features (Generate Video tab, Editor Lab, etc.)

Always aim to provide practical, helpful responses that guide users to successfully create their videos."""
        
        self.video_tips = [
            "For engaging videos, keep your intro under 5 seconds to hook viewers immediately.",
            "Use dynamic transitions between scenes to maintain viewer interest.",
            "Background music can increase engagement by up to 80% - choose tracks that match your video's mood.",
            "The rule of thirds helps create visually appealing compositions in your scenes.",
            "Short videos (30-60 seconds) tend to perform better on social media platforms.",
        ]
        
        self.creative_prompts = [
            "Try creating a video about: 'A journey through different seasons'",
            "How about: 'Urban life vs. Nature - A visual comparison'",
            "Consider: 'The beauty of golden hour photography'",
            "Idea: 'A day in the life of a busy city'",
            "Suggestion: 'Peaceful ocean waves at sunset'",
        ]
    
    def get_response(self, message, session_id='default', mode='smart'):
        """Generate AI-powered response to user message"""
        if session_id not in self.conversations:
            self.conversations[session_id] = {
                'history': [],
                'started': datetime.now().isoformat()
            }
        
        # Store user message
        self.conversations[session_id]['history'].append({
            'role': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate response
        if self.use_ai:
            response = self._generate_ai_response(message, session_id)
        else:
            response = self._generate_fallback_response(message.lower().strip())
        
        # Store assistant response
        self.conversations[session_id]['history'].append({
            'role': 'assistant',
            'message': response,
            'timestamp': datetime.now().isoformat()
        })
        
        return response
    
    def _generate_contextual_response(self, message_lower, session_id, mode):
        """Generate contextual response based on message content"""
        
        # Greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return "Hello! I'm your AI video creation assistant. I can help you with:\n\n• Generating video scripts\n• Finding the perfect visuals\n• Creating engaging content\n• Video editing tips\n• Creative ideas\n\nWhat would you like to create today?"
        
        # Help/What can you do
        if any(phrase in message_lower for phrase in ['what can you', 'help me', 'how to', 'can you help']):
            return "I'm here to help you create amazing videos! Here's what I can assist with:\n\n🎬 **Script Generation**: I can help write engaging video scripts\n🎨 **Visual Selection**: Find perfect images and videos from Pexels\n✂️ **Editing Tips**: Get advice on video editing and composition\n💡 **Creative Ideas**: Generate unique video concepts\n🎵 **Audio Guidance**: Tips for voiceovers and background music\n\nJust tell me what you're working on, and I'll guide you through it!"
        
        # Script-related questions
        if any(word in message_lower for word in ['script', 'write', 'story', 'narration', 'text']):
            return "I can help you with video scripts! Here are some tips:\n\n📝 **Keep it Concise**: Aim for 130-150 words per minute of video\n🎯 **Hook Early**: Grab attention in the first 3 seconds\n💬 **Conversational Tone**: Write like you're talking to a friend\n📊 **Structure**: Use intro, main content, and call-to-action\n\nHead to the 'Generate Video' tab and enter your topic - I'll create a professional script for you! What's your video about?"
        
        # Visual/Image questions
        if any(word in message_lower for word in ['image', 'photo', 'picture', 'visual', 'footage', 'video clip']):
            return "Looking for the perfect visuals? I've got you covered!\n\n🖼️ **High-Quality Sources**: I search Pexels for professional-grade content\n🎨 **Smart Matching**: I find visuals that match your script perfectly\n⚡ **Quick Selection**: Browse and pick exactly what you need\n\nGo to 'Generate Video' → Enter your prompt → Get curated visuals instantly!\n\nTip: Be specific with your descriptions (e.g., 'golden sunset over calm ocean' works better than just 'sunset')"
        
        # Editing questions
        if any(word in message_lower for word in ['edit', 'editing', 'trim', 'cut', 'editor', 'timeline']):
            return "The Editor Lab is perfect for video editing! Here's what you can do:\n\n✂️ **Trim Clips**: Adjust start/end points precisely\n⚡ **Speed Control**: Slow-mo or time-lapse effects\n🎚️ **Audio Mixing**: Adjust volume, add fade effects\n🎨 **Color Grading**: Brightness, contrast, and saturation\n🔄 **Rearrange**: Drag and drop clips on the timeline\n\nNavigate to 'Editor Lab' to start editing your videos!"
        
        # Creative ideas
        if any(word in message_lower for word in ['idea', 'creative', 'inspiration', 'suggest', 'topic']):
            tip = random.choice(self.creative_prompts)
            return f"Need creative inspiration? Here are some trending video ideas:\n\n{tip}\n\n🌟 Popular Themes:\n• Nature & Landscapes\n• Urban Exploration\n• Time-lapse Videos\n• Before & After Transformations\n• Day-in-the-Life Content\n\nWhat type of content interests you most?"
        
        # Tips/Advice
        if any(word in message_lower for word in ['tip', 'advice', 'best practice', 'recommend']):
            tip = random.choice(self.video_tips)
            return f"Here's a professional tip for you:\n\n💡 {tip}\n\nWant more specific advice? Ask me about:\n• Script writing\n• Visual composition\n• Audio selection\n• Video length\n• Engagement optimization"
        
        # Duration/Length questions
        if any(word in message_lower for word in ['long', 'duration', 'length', 'time', 'seconds', 'minutes']):
            return "Video length matters! Here's the sweet spot for different platforms:\n\n📱 **Instagram Reels**: 15-30 seconds (max 90s)\n📺 **YouTube Shorts**: 15-60 seconds\n🎵 **TikTok**: 15-60 seconds (up to 10 mins)\n📘 **Facebook**: 1-2 minutes\n🐦 **Twitter**: 30-45 seconds\n🎥 **YouTube Standard**: 7-15 minutes\n\nShorter videos (30-60s) generally have higher completion rates. What platform are you creating for?"
        
        # Music/Audio questions
        if any(word in message_lower for word in ['music', 'audio', 'sound', 'voice', 'narration']):
            return "Audio can make or break your video! Here's what to consider:\n\n🎵 **Background Music**: Choose royalty-free tracks that match your mood\n🎤 **Voiceover**: Use clear, enthusiastic narration (130-150 WPM)\n🔊 **Volume Balance**: Music at 20-30% volume when voice is present\n⚡ **Audio Sync**: Match music beats with visual transitions\n\nIn 'Generate Video', I'll create voice narration from your script automatically. You can also add background music in the Editor Lab!"
        
        # Export/Download questions
        if any(word in message_lower for word in ['export', 'download', 'save', 'render']):
            return "Ready to export your video? Here's the process:\n\n1️⃣ Complete your video in 'Editor Lab'\n2️⃣ Click the 'Export Video' button\n3️⃣ Wait for processing (usually 30-60 seconds)\n4️⃣ Download your MP4 file\n\n✨ Export settings:\n• Format: MP4 (H.264)\n• Resolution: Original quality\n• Audio: AAC, 192kbps\n\nYour video will be ready to upload anywhere!"
        
        # Thank you
        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! I'm always here to help you create amazing videos. 😊\n\nFeel free to ask me anything about:\n• Video creation\n• Script writing\n• Visual selection\n• Editing techniques\n\nHappy creating!"
        
        # Goodbye
        if any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'later']):
            return "Goodbye! Come back anytime you need help with video creation. Happy filming! 🎬✨"
        
        # General/Default response with context
        return self._generate_general_response(message_lower, session_id)
    
    def _generate_general_response(self, message_lower, session_id):
        """Generate a helpful general response"""
        
        # Check for questions
        if '?' in message_lower or any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', 'can']):
            return """I'd be happy to help! I specialize in video creation and can assist with:

🎬 **Video Generation**: Create complete videos from text prompts
✍️ **Script Writing**: Generate engaging narratives
🖼️ **Visual Content**: Find perfect images and video clips
✂️ **Editing**: Trim, adjust, and enhance your videos
💡 **Creative Ideas**: Brainstorm unique video concepts

Could you tell me more specifically what you'd like to create or learn about?"""
        
        # Conversational response
        responses = [
            f"I understand you're interested in '{message_lower[:50]}'. Let me help you with that!\n\nFor video creation, you can:\n• Generate scripts in the 'Generate Video' tab\n• Find visuals automatically\n• Edit videos in the 'Editor Lab'\n\nWhat aspect would you like to focus on?",
            
            f"Great topic! Here's how I can help with '{message_lower[:50]}':\n\n1. Create a detailed video script\n2. Find matching visuals from Pexels\n3. Generate professional voiceover\n4. Edit and export your final video\n\nShall we start with generating a script?",
            
            "That's an interesting idea! To create a video, I recommend:\n\n1️⃣ Start with a clear concept\n2️⃣ Generate a script (130-150 words/minute)\n3️⃣ Select engaging visuals\n4️⃣ Add audio and music\n5️⃣ Edit and export\n\nWould you like help with any of these steps?"
        ]
        
        return random.choice(responses)
    
    def clear_history(self, session_id='default'):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            return True
        return False
    
    def get_history(self, session_id='default'):
        """Get conversation history for a session"""
        return self.conversations.get(session_id, [])
