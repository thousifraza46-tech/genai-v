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
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.use_ai = True
            print("[Chatbot] ✅ Gemini AI initialized successfully (using gemini-2.0-flash)")
        except Exception as e:
            print(f"[Chatbot] ⚠️ AI initialization failed: {e}, using fallback responses")
            self.use_ai = False
        
        # System prompt for AI context
        self.system_context = """You are an intelligent and helpful AI assistant with strong comprehension skills.

Core Principles:
- LISTEN CAREFULLY: Read the user's message thoroughly to understand their actual intent
- CONTEXT AWARE: Consider previous messages in the conversation for better understanding
- RELEVANT RESPONSES: Provide answers that directly address what the user is asking
- NATURAL CONVERSATION: Don't force topics - follow the user's lead
- ASK WHEN UNCLEAR: If the request is ambiguous, ask clarifying questions

Video Platform Expertise (use when relevant):
You can help users with this video generation platform when they ask about:
- Writing video scripts and content
- Finding images/videos from Pexels
- Video editing techniques
- Creative ideas and brainstorming
- Platform features and how to use them

General Knowledge:
You can also discuss any other topics users bring up - technology, science, culture, entertainment, advice, or casual conversation. Provide accurate, helpful information on whatever they're interested in.

Response Style:
- Match the user's tone (formal, casual, technical, friendly)
- Be concise but complete - answer fully without being overly long
- Use formatting (bullet points, emojis) when it improves clarity
- Stay helpful, patient, and encouraging"""
        
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
    
    def _generate_ai_response(self, message, session_id):
        """Generate response using Gemini AI with conversation context"""
        try:
            # Build conversation context
            history = self.conversations[session_id]['history']
            context_messages = []
            
            # Include last 10 exchanges for context (20 messages = 10 back-and-forth)
            recent_history = history[-20:] if len(history) > 20 else history
            
            for msg in recent_history:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context_messages.append(f"{role}: {msg['message']}")
            
            # Build full prompt with system context and conversation history
            full_prompt = f"""{self.system_context}

Previous conversation:
{chr(10).join(context_messages) if context_messages else 'This is the start of the conversation.'}

Current user message: {message}

Instructions:
1. Read and understand what the user is actually asking or trying to say
2. Consider the context from previous messages if relevant
3. Provide a direct, helpful, and accurate response to their specific question or request
4. If the user is asking about video creation, provide detailed guidance
5. If asking about other topics, respond naturally and informatively
6. Match the tone and formality level of the user's message
7. If the request is unclear, ask clarifying questions

Your response:"""
            
            # Generate AI response with improved settings
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,  # Balanced creativity and accuracy
                    'top_p': 0.9,
                    'top_k': 40,
                    'max_output_tokens': 1024,
                }
            )
            return response.text.strip()
            
        except Exception as e:
            print(f"[Chatbot] Error generating AI response: {e}")
            # Fallback to rule-based response
            return self._generate_fallback_response(message.lower().strip())
    
    def _generate_fallback_response(self, message_lower):
        """Generate fallback response when AI is unavailable (rule-based)"""
        
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
        
        # General/Default response
        return "I'm your AI video creation assistant! I can help you with:\n\n✨ **Script Writing**: Create engaging video scripts\n🎨 **Visual Selection**: Find perfect images and videos\n✂️ **Video Editing**: Tips and techniques for polished videos\n💡 **Creative Ideas**: Brainstorm unique video concepts\n\nWhat would you like to know more about?"
    
    def get_history(self, session_id='default'):
        """Get conversation history for a session"""
        if session_id in self.conversations:
            return self.conversations[session_id].get('history', [])
        return []
    
    def clear_history(self, session_id='default'):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            self.conversations[session_id] = {
                'history': [],
                'started': datetime.now().isoformat()
            }
            return True
        return False

