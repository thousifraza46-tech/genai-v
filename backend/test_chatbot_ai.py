#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for AI-powered chatbot
"""
from chatbot_engine import ChatbotEngine
import time

def test_chatbot():
    print("=" * 60)
    print("🧪 Testing AI-Powered Chatbot")
    print("=" * 60)
    
    # Initialize chatbot
    chatbot = ChatbotEngine()
    
    if chatbot.use_ai:
        print("✅ Gemini AI is active\n")
    else:
        print("⚠️ Using fallback mode (AI unavailable)\n")
    
    # Test queries
    test_queries = [
        "Hello! Can you help me?",
        "I want to create a video about travel destinations",
        "What makes a good video hook?",
        "How long should my video be for Instagram?"
    ]
    
    session_id = "test_session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 60}")
        print(f"Query {i}: {query}")
        print(f"{'-' * 60}")
        
        start_time = time.time()
        response = chatbot.get_response(query, session_id=session_id)
        end_time = time.time()
        
        print(f"Response ({end_time - start_time:.2f}s):")
        print(response)
        print(f"{'=' * 60}\n")
    
    # Test conversation history
    print("\n" + "=" * 60)
    print("📜 Conversation History:")
    print("=" * 60)
    history = chatbot.get_history(session_id)
    print(f"Total messages: {len(history)}")
    
    print("\n✅ Chatbot test complete!")

if __name__ == "__main__":
    test_chatbot()
