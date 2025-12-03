"""
Scene Segmentation Module
Splits scripts into logical scenes for better video structure
"""

import re
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def split_script_to_scenes(text: str, max_words_per_scene: int = 50) -> List[Dict[str, any]]:
    """
    Split script into logical scenes based on sentence boundaries
    
    Args:
        text: Input script text
        max_words_per_scene: Maximum words per scene
        
    Returns:
        List of scene dictionaries with text and metadata
    """
    try:
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        
        scenes = []
        current_scene = ""
        current_word_count = 0
        scene_number = 1
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_words = len(sentence.split())
            
            if current_word_count + sentence_words > max_words_per_scene and current_scene:
                scenes.append({
                    "scene_number": scene_number,
                    "text": current_scene.strip(),
                    "word_count": current_word_count,
                    "estimated_duration": estimate_duration(current_word_count)
                })
                scene_number += 1
                current_scene = sentence
                current_word_count = sentence_words
            else:
                current_scene = (current_scene + " " + sentence).strip()
                current_word_count += sentence_words
        
        if current_scene:
            scenes.append({
                "scene_number": scene_number,
                "text": current_scene.strip(),
                "word_count": current_word_count,
                "estimated_duration": estimate_duration(current_word_count)
            })
        
        logger.info(f"Split script into {len(scenes)} scenes")
        return scenes
        
    except Exception as e:
        logger.error(f"Error splitting script: {e}")
        return [{
            "scene_number": 1,
            "text": text,
            "word_count": len(text.split()),
            "estimated_duration": estimate_duration(len(text.split()))
        }]

def estimate_duration(word_count: int, words_per_minute: int = 140) -> float:
    """
    Estimate scene duration based on word count
    
    Args:
        word_count: Number of words
        words_per_minute: Average speaking rate
        
    Returns:
        Estimated duration in seconds
    """
    return max(3.0, (word_count / words_per_minute) * 60)

def build_transition_plan(style: str, scene_count: int) -> List[Dict[str, any]]:
    """
    Create transition effects plan based on video style
    
    Args:
        style: Video style (cinematic, documentary, educational, etc.)
        transition_count: Number of transitions needed
        
    Returns:
        List of transition configurations
    """
    if scene_count <= 1:
        return []
    
    transition_count = scene_count - 1
    
    transitions_map = {
        "cinematic": [
            {"type": "crossfade", "duration": 1.0, "easing": "ease-in-out"}
        ] * transition_count,
        
        "documentary": [
            {"type": "cut", "duration": 0.0, "easing": "linear"}
        ] * transition_count,
        
        "educational": [
            {"type": "fade", "duration": 0.5, "easing": "ease-out"}
        ] * transition_count,
        
        "dynamic": [
            {"type": "slide", "duration": 0.7, "easing": "ease-in-out"}
        ] * transition_count,
        
        "news": [
            {"type": "cut", "duration": 0.0, "easing": "linear"}
        ] * transition_count,
    }
    
    return transitions_map.get(style, transitions_map["documentary"])

def get_scene_summary(scenes: List[Dict[str, any]]) -> Dict[str, any]:
    """
    Get summary statistics about scenes
    
    Args:
        scenes: List of scene dictionaries
        
    Returns:
        Summary statistics
    """
    if not scenes:
        return {
            "total_scenes": 0,
            "total_words": 0,
            "total_duration": 0.0,
            "avg_scene_duration": 0.0
        }
    
    total_words = sum(s["word_count"] for s in scenes)
    total_duration = sum(s["estimated_duration"] for s in scenes)
    
    return {
        "total_scenes": len(scenes),
        "total_words": total_words,
        "total_duration": round(total_duration, 1),
        "avg_scene_duration": round(total_duration / len(scenes), 1),
        "min_scene_words": min(s["word_count"] for s in scenes),
        "max_scene_words": max(s["word_count"] for s in scenes)
    }
