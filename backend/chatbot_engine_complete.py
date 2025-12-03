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

User: {message}