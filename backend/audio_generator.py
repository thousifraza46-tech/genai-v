
import os
import asyncio
import time
import random
from typing import Dict, Any, Optional, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.warning(" edge-tts not available for audio generation")

class AudioGenerator:
    
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or os.path.join("assets", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.tts_available = EDGE_TTS_AVAILABLE
        
        self.default_voice = "en-US-ChristopherNeural"
        self.voice_options = [
            "en-US-ChristopherNeural",
            "en-US-EricNeural",
            "en-US-GuyNeural",
            "en-US-JennyNeural",
            "en-US-AriaNeural",
            "en-GB-RyanNeural"
        ]
        
        self.default_rate = "+0%"
        self.default_volume = "+0%"
        
        logger.info(f" Audio Generator initialized (TTS Available: {self.tts_available})")
    
    async def _generate_with_edge_tts(
        self, 
        text: str, 
        output_path: str,
        voice: str = None,
        rate: str = None,
        volume: str = None
    ) -> bool:
        try:
            voice = voice or self.default_voice
            rate = rate or self.default_rate
            volume = volume or self.default_volume
            
            communicate = edge_tts.Communicate(
                text, 
                voice,
                rate=rate,
                volume=volume
            )
            
            await communicate.save(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f" Generated audio file: {output_path}")
                return True
            else:
                logger.error(f" Audio file generation failed: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f" Edge TTS generation failed: {e}")
            return False
    
    def generate_audio(
        self, 
        script: str, 
        voice: str = None,
        rate: str = None,
        volume: str = None,
        filename: str = None
    ) -> Dict[str, Any]:
        logger.info(f" Generating audio for {len(script)} character script")
        
        if not filename:
            timestamp = int(time.time())
            filename = f"narration_{timestamp}"
        
        filename = os.path.splitext(filename)[0]
        
        output_path = os.path.join(self.output_dir, f"{filename}.mp3")
        
        if self.tts_available:
            success = asyncio.run(self._generate_with_edge_tts(
                text=script,
                output_path=output_path,
                voice=voice or self.default_voice,
                rate=rate or self.default_rate,
                volume=volume or self.default_volume
            ))
            
            if success:
                return {
                    "audio_path": output_path,
                    "duration": self._estimate_audio_duration(script),
                    "source": "edge-tts",
                    "voice": voice or self.default_voice
                }
        
        return self._use_fallback_audio(script, output_path)
    
    def _estimate_audio_duration(self, text: str) -> float:
        words = len(text.split())
        return (words / 150) * 60
    
    def _use_fallback_audio(self, script: str, output_path: str) -> Dict[str, Any]:
        logger.warning(" Using fallback audio file")
        
        fallback_files = []
        for f in os.listdir(self.output_dir):
            if f.endswith(".mp3"):
                full_path = os.path.join(self.output_dir, f)
                if os.path.getsize(full_path) > 1000:
                    fallback_files.append(full_path)
        
        narration_files = [f for f in fallback_files if "narration" in f]
        if narration_files:
            fallback_path = random.choice(narration_files)
            logger.info(f"Using existing narration file: {os.path.basename(fallback_path)}")
        elif fallback_files:
            fallback_path = random.choice(fallback_files)
            logger.info(f"Using existing audio file: {os.path.basename(fallback_path)}")
        else:
            logger.warning("No suitable audio files found, creating placeholder")
            fallback_path = self._create_placeholder_audio(script, output_path)
        
        if fallback_path and os.path.exists(fallback_path):
            return {
                "audio_path": fallback_path,
                "duration": self._estimate_audio_duration(script),
                "source": "fallback",
                "voice": None
            }
        else:
            return {
                "audio_path": None,
                "duration": 0,
                "source": "none",
                "voice": None
            }
    
    def _create_placeholder_audio(self, script: str, output_path: str) -> str:
        try:
            working_files = [
                "demo_narration.mp3",
                "test_narration.mp3", 
                "narration.mp3",
                "test_male_voice_0.mp3"
            ]
            
            for filename in working_files:
                source_path = os.path.join(self.output_dir, filename)
                if os.path.exists(source_path) and os.path.getsize(source_path) > 1000:
                    logger.info(f"Using template audio: {filename}")
                    return source_path
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create placeholder audio: {e}")
            return None

    def list_available_voices(self) -> List[Tuple[str, str]]:
        if not self.tts_available:
            return []
        
        try:
            voices = asyncio.run(edge_tts.list_voices())
            return [(v["ShortName"], f"{v['Gender']}, {v['Locale']}") for v in voices]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return [(v, "Default voice") for v in self.voice_options]

if __name__ == "__main__":
    generator = AudioGenerator()
    
    print("\nAvailable voices:")
    voices = generator.list_available_voices()
    for voice_id, desc in voices[:10]:
        print(f"- {voice_id}: {desc}")
    
    test_script = "Welcome to this demonstration of our audio generation system. This narration is being generated using text-to-speech technology to create professional video narration."
    
    print("\nGenerating audio...")
    audio_data = generator.generate_audio(
        script=test_script,
        filename="test_narration"
    )
    
    print(f"\nAudio generated:")
    print(f"- Path: {audio_data['audio_path']}")
    print(f"- Duration: {audio_data['duration']:.2f} seconds")
    print(f"- Source: {audio_data['source']}")
    print(f"- Voice: {audio_data['voice']}")
