"""
Video Quality Evaluation Module
Provides metrics for assessing video quality
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

def evaluate_video_quality(
    video_path: Optional[str],
    audio_path: Optional[str],
    script_text: Optional[str],
    generation_time: Optional[float] = None
) -> Dict[str, any]:
    """
    Evaluate video generation quality with various metrics
    
    Args:
        video_path: Path to generated video
        audio_path: Path to generated audio
        script_text: Original script text
        generation_time: Time taken to generate (seconds)
        
    Returns:
        Dictionary of quality metrics
    """
    metrics = {
        "video_exists": False,
        "audio_exists": False,
        "video_size_mb": 0.0,
        "audio_size_mb": 0.0,
        "script_words": 0,
        "script_characters": 0,
        "generation_time_seconds": generation_time or 0.0,
        "quality_score": 0.0,
        "issues": []
    }
    
    try:
        if video_path and os.path.exists(video_path):
            metrics["video_exists"] = True
            video_size = os.path.getsize(video_path)
            metrics["video_size_mb"] = round(video_size / (1024 * 1024), 2)
            
            try:
                from moviepy import VideoFileClip
                with VideoFileClip(video_path) as clip:
                    metrics["video_duration"] = round(clip.duration, 2)
                    metrics["video_resolution"] = clip.size
                    metrics["video_fps"] = clip.fps
            except:
                pass
        else:
            metrics["issues"].append("Video file not found")
        
        if audio_path and os.path.exists(audio_path):
            metrics["audio_exists"] = True
            audio_size = os.path.getsize(audio_path)
            metrics["audio_size_mb"] = round(audio_size / (1024 * 1024), 2)
            
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(audio_path)
                metrics["audio_duration"] = round(len(audio) / 1000.0, 2)
            except:
                pass
        else:
            metrics["issues"].append("Audio file not found")
        
        if script_text:
            metrics["script_words"] = len(script_text.split())
            metrics["script_characters"] = len(script_text)
        else:
            metrics["issues"].append("No script provided")
        
        quality_score = 0.0
        if metrics["video_exists"]:
            quality_score += 40
        if metrics["audio_exists"]:
            quality_score += 30
        if metrics["script_words"] > 0:
            quality_score += 20
        if metrics.get("video_duration", 0) > 0:
            quality_score += 10
        
        metrics["quality_score"] = quality_score
        
        if quality_score >= 90:
            metrics["quality_rating"] = "Excellent"
        elif quality_score >= 70:
            metrics["quality_rating"] = "Good"
        elif quality_score >= 50:
            metrics["quality_rating"] = "Fair"
        else:
            metrics["quality_rating"] = "Poor"
        
        logger.info(f"Quality evaluation complete: {metrics['quality_rating']} ({quality_score}%)")
        
    except Exception as e:
        logger.error(f"Error evaluating quality: {e}")
        metrics["issues"].append(f"Evaluation error: {str(e)}")
    
    return metrics

def calculate_sync_score(video_duration: float, audio_duration: float) -> Dict[str, any]:
    """
    Calculate audio-video synchronization score
    
    Args:
        video_duration: Video duration in seconds
        audio_duration: Audio duration in seconds
        
    Returns:
        Sync metrics
    """
    if video_duration == 0 or audio_duration == 0:
        return {
            "sync_score": 0.0,
            "sync_rating": "Unknown",
            "duration_diff": 0.0
        }
    
    duration_diff = abs(video_duration - audio_duration)
    duration_diff_percent = (duration_diff / max(video_duration, audio_duration)) * 100
    
    if duration_diff_percent < 5:
        sync_rating = "Excellent"
        sync_score = 100.0
    elif duration_diff_percent < 10:
        sync_rating = "Good"
        sync_score = 80.0
    elif duration_diff_percent < 20:
        sync_rating = "Fair"
        sync_score = 60.0
    else:
        sync_rating = "Poor"
        sync_score = 40.0
    
    return {
        "sync_score": sync_score,
        "sync_rating": sync_rating,
        "duration_diff": round(duration_diff, 2),
        "duration_diff_percent": round(duration_diff_percent, 2)
    }

def estimate_optimal_duration(script_text: str, words_per_minute: int = 140) -> Dict[str, float]:
    """
    Estimate optimal video duration from script
    
    Args:
        script_text: Script text
        words_per_minute: Average speaking rate
        
    Returns:
        Duration estimates
    """
    if not script_text:
        return {
            "min_duration": 5.0,
            "optimal_duration": 10.0,
            "max_duration": 15.0
        }
    
    word_count = len(script_text.split())
    
    base_duration = (word_count / words_per_minute) * 60
    
    min_duration = max(5.0, base_duration * 0.9)
    optimal_duration = max(10.0, base_duration)
    max_duration = base_duration * 1.2
    
    return {
        "min_duration": round(min_duration, 1),
        "optimal_duration": round(optimal_duration, 1),
        "max_duration": round(max_duration, 1),
        "words_per_minute": words_per_minute
    }
