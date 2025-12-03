"""
Emotion and Tone Detection Module
Analyzes text sentiment and emotion to guide music, voice, and visual choices
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmotionDetector:
    """Detects emotion and sentiment from text using transformer models"""
    
    def __init__(self):
        self.sentiment_analyzer = None
        self.emotion_classifier = None
        self._initialized = False
        
    def initialize(self):
        """Load models lazily to improve startup time"""
        if self._initialized:
            return
            
        try:
            from transformers import pipeline
            
            logger.info("Loading sentiment analysis model...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            logger.info("Loading emotion classification model...")
            self.emotion_classifier = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base",
                top_k=None
            )
            
            self._initialized = True
            logger.info("Emotion detection models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize emotion detection: {e}")
            self._initialized = False
    
    def analyze_tone(self, text: str) -> Dict[str, str]:
        """
        Analyze emotional tone of text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment, emotion, music_mood, and color_theme
        """
        if not self._initialized:
            self.initialize()
        
        if not self._initialized:
            return self._get_default_tone()
        
        try:
            truncated_text = text[:512]
            
            sentiment_result = self.sentiment_analyzer(truncated_text)[0]
            sentiment = sentiment_result["label"].lower()
            
            emotion_results = self.emotion_classifier(truncated_text)[0]
            top_emotion = sorted(emotion_results, key=lambda x: x["score"], reverse=True)[0]
            emotion = top_emotion["label"].lower()
            
            music_mood = self._determine_music_mood(emotion)
            color_theme = self._determine_color_theme(music_mood)
            voice_style = self._determine_voice_style(emotion, sentiment)
            
            return {
                "sentiment": sentiment,
                "emotion": emotion,
                "emotion_score": round(top_emotion["score"], 3),
                "music_mood": music_mood,
                "color_theme": color_theme,
                "voice_style": voice_style
            }
            
        except Exception as e:
            logger.error(f"Error analyzing tone: {e}")
            return self._get_default_tone()
    
    def _determine_music_mood(self, emotion: str) -> str:
        """Map emotion to music mood"""
        mood_map = {
            "sadness": "calm",
            "fear": "calm",
            "anger": "intense",
            "joy": "uplifting",
            "love": "uplifting",
            "surprise": "energetic",
            "neutral": "neutral"
        }
        return mood_map.get(emotion, "neutral")
    
    def _determine_color_theme(self, music_mood: str) -> str:
        """Map music mood to color theme"""
        color_map = {
            "calm": "cool",
            "uplifting": "warm",
            "intense": "dark",
            "energetic": "vibrant",
            "neutral": "neutral"
        }
        return color_map.get(music_mood, "neutral")
    
    def _determine_voice_style(self, emotion: str, sentiment: str) -> str:
        """Determine recommended voice narration style"""
        if emotion in ["sadness", "fear"]:
            return "gentle"
        elif emotion in ["joy", "love"]:
            return "cheerful"
        elif emotion == "anger":
            return "serious"
        elif sentiment == "positive":
            return "friendly"
        else:
            return "neutral"
    
    def _get_default_tone(self) -> Dict[str, str]:
        """Return default tone when analysis fails"""
        return {
            "sentiment": "neutral",
            "emotion": "neutral",
            "emotion_score": 0.0,
            "music_mood": "neutral",
            "color_theme": "neutral",
            "voice_style": "neutral"
        }


_detector = EmotionDetector()

def analyze_tone(text: str) -> Dict[str, str]:
    """
    Convenience function for emotion analysis
    
    Args:
        text: Text to analyze
        
    Returns:
        Emotion analysis results
    """
    return _detector.analyze_tone(text)
