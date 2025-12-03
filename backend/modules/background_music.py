"""
Background Music Module
Manages background music selection and audio mixing
"""

import os
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

MUSIC_LIBRARY = {
    "calm": "calm.mp3",
    "uplifting": "uplifting.mp3",
    "intense": "intense.mp3",
    "energetic": "energetic.mp3",
    "neutral": "neutral.mp3"
}

def get_music_path(mood: str) -> Optional[str]:
    """
    Get path to background music file for given mood
    
    Args:
        mood: Music mood (calm, uplifting, intense, etc.)
        
    Returns:
        Path to music file or None if not found
    """
    music_dir = Path("assets/music")
    
    filename = MUSIC_LIBRARY.get(mood, MUSIC_LIBRARY["neutral"])
    music_path = music_dir / filename
    
    if music_path.exists():
        return str(music_path)
    
    for filename in MUSIC_LIBRARY.values():
        alt_path = music_dir / filename
        if alt_path.exists():
            logger.warning(f"Mood '{mood}' not found, using {filename}")
            return str(alt_path)
    
    logger.warning(f"No background music found for mood: {mood}")
    return None

def mix_audio_with_music(
    narration_path: str,
    music_path: Optional[str],
    output_path: str,
    music_volume_reduction_db: int = 18
) -> str:
    """
    Mix narration audio with background music
    
    Args:
        narration_path: Path to narration audio
        music_path: Path to background music
        output_path: Path for output mixed audio
        music_volume_reduction_db: How much to reduce music volume (in dB)
        
    Returns:
        Path to mixed audio file
    """
    if not music_path or not os.path.exists(music_path):
        logger.info("No background music to mix")
        return narration_path
    
    if not os.path.exists(narration_path):
        logger.error(f"Narration file not found: {narration_path}")
        return narration_path
    
    try:
        from pydub import AudioSegment
        
        logger.info(f"Mixing narration with background music...")
        
        narration = AudioSegment.from_file(narration_path)
        music = AudioSegment.from_file(music_path)
        
        music = music - abs(music_volume_reduction_db)
        
        narration_duration = len(narration)
        
        if len(music) < narration_duration:
            loops_needed = int(narration_duration / len(music)) + 1
            music = music * loops_needed
        
        music = music[:narration_duration]
        
        mixed = music.overlay(narration)
        
        mixed.export(output_path, format="mp3")
        
        logger.info(f"Audio mixed successfully: {output_path}")
        return output_path
        
    except ImportError:
        logger.warning("pydub not installed, skipping music mixing")
        return narration_path
    except Exception as e:
        logger.error(f"Error mixing audio: {e}")
        return narration_path

def create_music_directory():
    """Create music assets directory if it doesn't exist"""
    music_dir = Path("assets/music")
    music_dir.mkdir(parents=True, exist_ok=True)
    
    readme_path = music_dir / "README.txt"
    if not readme_path.exists():
        with open(readme_path, 'w') as f:
            f.write("Background Music Library\n")
            f.write("=" * 40 + "\n\n")
            f.write("Place your background music files here:\n\n")
            for mood, filename in MUSIC_LIBRARY.items():
                f.write(f"  {filename} - For {mood} scenes\n")
            f.write("\nSupported formats: MP3, WAV, OGG\n")
            f.write("Recommended: Instrumental, royalty-free music\n")
    
    logger.info(f"Music directory ready: {music_dir}")

create_music_directory()
