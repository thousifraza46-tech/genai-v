"""
Multilingual Support Module
Provides translation and language-specific voice selection
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "voices": ["en-US-AriaNeural", "en-US-GuyNeural", "en-GB-SoniaNeural"],
        "default_voice": "en-US-AriaNeural"
    },
    "hi": {
        "name": "Hindi",
        "voices": ["hi-IN-SwaraNeural", "hi-IN-MadhurNeural"],
        "default_voice": "hi-IN-SwaraNeural"
    },
    "ta": {
        "name": "Tamil",
        "voices": ["ta-IN-PallaviNeural", "ta-IN-ValluvarNeural"],
        "default_voice": "ta-IN-PallaviNeural"
    },
    "kn": {
        "name": "Kannada",
        "voices": ["kn-IN-SapnaNeural", "kn-IN-GaganNeural"],
        "default_voice": "kn-IN-SapnaNeural"
    },
    "te": {
        "name": "Telugu",
        "voices": ["te-IN-ShrutiNeural", "te-IN-MohanNeural"],
        "default_voice": "te-IN-ShrutiNeural"
    },
    "ml": {
        "name": "Malayalam",
        "voices": ["ml-IN-SobhanaNeural", "ml-IN-MidhunNeural"],
        "default_voice": "ml-IN-SobhanaNeural"
    },
    "es": {
        "name": "Spanish",
        "voices": ["es-ES-ElviraNeural", "es-MX-DaliaNeural"],
        "default_voice": "es-ES-ElviraNeural"
    },
    "fr": {
        "name": "French",
        "voices": ["fr-FR-DeniseNeural", "fr-FR-HenriNeural"],
        "default_voice": "fr-FR-DeniseNeural"
    },
    "de": {
        "name": "German",
        "voices": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
        "default_voice": "de-DE-KatjaNeural"
    },
    "ja": {
        "name": "Japanese",
        "voices": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
        "default_voice": "ja-JP-NanamiNeural"
    },
    "zh": {
        "name": "Chinese",
        "voices": ["zh-CN-XiaoxiaoNeural", "zh-CN-YunxiNeural"],
        "default_voice": "zh-CN-XiaoxiaoNeural"
    },
    "ar": {
        "name": "Arabic",
        "voices": ["ar-SA-ZariyahNeural", "ar-SA-HamedNeural"],
        "default_voice": "ar-SA-ZariyahNeural"
    }
}

def translate_text(text: str, target_language: str, source_language: str = "auto") -> str:
    """
    Translate text to target language
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'hi', 'ta')
        source_language: Source language code (default: auto-detect)
        
    Returns:
        Translated text or original if translation fails
    """
    if target_language == "en" or target_language not in SUPPORTED_LANGUAGES:
        return text
    
    try:
        from deep_translator import GoogleTranslator
        
        lang_map = {
            "hi": "hi",  # Hindi
            "ta": "ta",  # Tamil
            "kn": "kn",  # Kannada
            "te": "te",  # Telugu
            "ml": "ml",  # Malayalam
            "es": "es",  # Spanish
            "fr": "fr",  # French
            "de": "de",  # German
            "ja": "ja",  # Japanese
            "zh": "zh-CN",  # Chinese Simplified
            "ar": "ar"   # Arabic
        }
        
        google_lang_code = lang_map.get(target_language, target_language)
        
        translator = GoogleTranslator(source='auto', target=google_lang_code)
        
        max_chunk_size = 4500
        if len(text) <= max_chunk_size:
            translated = translator.translate(text)
            if translated and translated != text:
                logger.info(f"✓ Successfully translated to {target_language}: '{text[:50]}...' → '{translated[:50]}...'")
                return translated
            else:
                logger.warning(f"Translation returned same text for {target_language}")
                return text
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        translated_chunks = []
        for chunk in chunks:
            translated_chunk = translator.translate(chunk)
            translated_chunks.append(translated_chunk)
        
        translated_text = " ".join(translated_chunks)
        logger.info(f"✓ Translated {len(chunks)} chunks to {target_language}")
        return translated_text
        
    except ImportError as e:
        logger.error(f"❌ deep-translator not installed: {e}")
        logger.error(f"   Install with: pip install deep-translator")
        return text
    except Exception as e:
        logger.error(f"❌ Translation failed for {target_language}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return text

def get_voice_for_language(language: str, voice_style: str = "neutral") -> str:
    """
    Get appropriate voice for language and style
    
    Args:
        language: Language code
        voice_style: Voice style preference (neutral, friendly, etc.)
        
    Returns:
        Voice name for Edge TTS
    """
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    
    lang_config = SUPPORTED_LANGUAGES[language]
    
    return lang_config["default_voice"]

def get_language_info(language: str) -> Dict[str, any]:
    """
    Get information about a language
    
    Args:
        language: Language code
        
    Returns:
        Language configuration dictionary
    """
    return SUPPORTED_LANGUAGES.get(language, SUPPORTED_LANGUAGES["en"])

def get_supported_languages() -> Dict[str, str]:
    """
    Get list of supported languages
    
    Returns:
        Dictionary mapping language codes to names
    """
    return {code: info["name"] for code, info in SUPPORTED_LANGUAGES.items()}
