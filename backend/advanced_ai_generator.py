
import os
import time
import logging
import asyncio
import requests
import json
import base64
import hashlib
from typing import Dict, Optional, List, Any
from pathlib import Path
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_keywords_for_pexels(user_prompt: str, max_keywords: int = 6) -> str:
    """
    Extract clean, contextual keywords from user prompt for Pexels API search.
    Improved to maintain context and key descriptive phrases.
    
    Args:
        user_prompt: The full user input prompt
        max_keywords: Maximum number of keywords to return (default: 6, increased for better accuracy)
    
    Returns:
        Clean keyword string suitable for Pexels search with preserved context
    
    Example:
        Input: "a happy dog running in a park on a sunny day"
        Output: "happy dog running park sunny day"
    """
    try:
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        import re
        
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            stop_words = set(stopwords.words('english'))
        
        custom_stop_words = {'video', 'create', 'make', 'show', 'generate', 'using', 'footage', 'clip'}
        stop_words.update(custom_stop_words)
        
        text_lower = user_prompt.lower()
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        
        try:
            words = word_tokenize(text_clean)
        except LookupError:
            nltk.download('punkt', quiet=True)
            words = word_tokenize(text_clean)
        
        keywords = []
        important_modifiers = {'beautiful', 'stunning', 'amazing', 'vibrant', 'peaceful', 'dramatic', 
                              'modern', 'ancient', 'natural', 'urban', 'rural', 'wild', 'calm', 
                              'colorful', 'bright', 'dark', 'night', 'day', 'sunset', 'sunrise'}
        
        for word in words:
            if (word.isalpha() and len(word) > 2):
                if word in important_modifiers:
                    keywords.append(word)
                elif word not in stop_words:
                    keywords.append(word)
        
        if len(keywords) > max_keywords:
            preserved_keywords = []
            for word in keywords:
                if word in important_modifiers and len(preserved_keywords) < max_keywords:
                    preserved_keywords.append(word)
            
            remaining_slots = max_keywords - len(preserved_keywords)
            for word in keywords:
                if word not in preserved_keywords and len(preserved_keywords) < max_keywords:
                    preserved_keywords.append(word)
            
            keywords = preserved_keywords
        
        keyword_string = ' '.join(keywords[:max_keywords])
        
        logger.info(f" Extracted keywords: '{user_prompt[:50]}...' -> '{keyword_string}'")
        
        return keyword_string if keyword_string else user_prompt
        
    except Exception as e:
        logger.warning(f"Keyword extraction failed: {e}, using original prompt")
        return user_prompt

try:
    from pexels_video_generator import process_prompt_for_pexels
except ImportError:
    def process_prompt_for_pexels(prompt: str):
        return extract_keywords_for_pexels(prompt), {}

class AdvancedAIMediaGenerator:
    
    def __init__(self):
        logger.info(" Initializing Advanced AI Media Generator...")
        
        for directory in ['assets/scripts', 'assets/audio', 'assets/videos', 'assets/images', 'assets/cache']:
            os.makedirs(directory, exist_ok=True)
        
        self.load_api_keys()
        
        self.setup_ai_clients()
        
        self._cache = {}
        self._cache_file = "assets/cache/generation_cache.json"
        self._load_cache()
        
        logger.info(" Advanced AI Media Generator ready!")
    
    def _load_cache(self):
        """Load persistent cache from disk"""
        try:
            if os.path.exists(self._cache_file):
                with open(self._cache_file, 'r') as f:
                    self._cache = json.load(f)
                logger.info(f" Loaded {len(self._cache)} cached items")
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
            self._cache = {}
    
    def _save_cache(self):
        """Save cache to disk"""
        try:
            with open(self._cache_file, 'w') as f:
                json.dump(self._cache, f)
        except Exception as e:
            logger.warning(f"Cache save failed: {e}")
    
    def _get_cache_key(self, prompt: str, method: str) -> str:
        """Generate cache key from prompt and method"""
        return hashlib.md5(f"{prompt}:{method}".encode()).hexdigest()

    def load_api_keys(self):
        try:
            from config import (
                GOOGLE_API_KEY, GEMINI_API_KEY,
                REPLICATE_API_TOKEN, RUNWAY_API_KEY, STABILITY_API_KEY,
                PEXELS_API_KEY
            )
            
            self.google_key = GOOGLE_API_KEY or GEMINI_API_KEY
            self.replicate_key = REPLICATE_API_TOKEN
            self.runway_key = RUNWAY_API_KEY
            self.stability_key = STABILITY_API_KEY
            self.pexels_key = PEXELS_API_KEY
            
            logger.info(" API keys loaded")
            
        except Exception as e:
            logger.error(f" Failed to load API keys: {e}")
            self.google_key = None
            self.replicate_key = None
            self.runway_key = None
            self.stability_key = None
            self.pexels_key = None

    def setup_ai_clients(self):
        if self.google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.google_key)
                try:
                    self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info(" Gemini AI initialized (gemini-1.5-flash)")
                except:
                    try:
                        self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
                        logger.info(" Gemini AI initialized (gemini-1.5-pro)")
                    except:
                        self.gemini_model = genai.GenerativeModel('models/gemini-1.5-flash')
                        logger.info(" Gemini AI initialized (models/gemini-1.5-flash)")
            except Exception as e:
                logger.warning(f"Gemini setup failed: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        if self.replicate_key:
            try:
                import replicate
                self.replicate_client = replicate.Client(api_token=self.replicate_key)
                logger.info(" Replicate client initialized")
            except Exception as e:
                logger.warning(f"Replicate setup failed: {e}")
                self.replicate_client = None
        else:
            self.replicate_client = None
        
        try:
            import edge_tts
            self.edge_tts = edge_tts
            self.voices = [
                'en-US-AriaNeural',
                'en-US-ChristopherNeural',
                'en-US-JennyNeural',
                'en-US-DavisNeural'
            ]
            logger.info(" Edge TTS initialized")
        except Exception as e:
            logger.warning(f"Edge TTS setup failed: {e}")
            self.edge_tts = None
            
        try:
            from pexels_video_generator import PexelsVideoGenerator
            self.pexels_video_generator = PexelsVideoGenerator(api_key=self.pexels_key)
            logger.info(" Pexels Video Generator initialized")
        except Exception as e:
            logger.warning(f"Pexels Video Generator setup failed: {e}")
            self.pexels_video_generator = None

    def generate_script(self, prompt: str) -> str:
        return self.generate_enhanced_script(prompt)
    
    def generate_enhanced_script(self, prompt: str) -> str:
        try:
            if self.gemini_model:
                enhanced_prompt = f"""
You are a professional video scriptwriter. Create a detailed, cinematic narration script.

USER'S EXACT VISUAL REQUEST: "{prompt}"

CRITICAL REQUIREMENTS:
1. The script MUST describe exactly what the user specified
2. Preserve ALL visual details from the user's prompt (colors, objects, settings, mood)
3. Expand on the description while staying 100% faithful to the original intent
4. Use cinematic, descriptive language
5. Length: 80-120 words for natural narration
6. Focus on visual elements that can be found in stock footage or generated by AI

Example:
User: "A tropical paradise with crystal clear turquoise water and palm trees"
Script: "Welcome to a breathtaking tropical paradise, where crystal clear turquoise water 
stretches endlessly toward the horizon. Majestic palm trees sway gently in the warm breeze, 
their fronds dancing against a brilliant blue sky. The pristine white sand beach glistens 
under the golden sun, creating a perfect sanctuary of natural beauty and tranquility."

Now create a script for the user's request. Write ONLY the narration script, no labels or extra text:
"""
                
                response = self.gemini_model.generate_content(enhanced_prompt)
                script = response.text.strip()
                
                prompt_lower = prompt.lower()
                script_lower = script.lower()
                
                import re
                prompt_words = set(re.findall(r'\b\w{4,}\b', prompt_lower))
                script_words = set(re.findall(r'\b\w{4,}\b', script_lower))
                
                if prompt_words and len(prompt_words & script_words) / len(prompt_words) >= 0.5:
                    logger.info(f" Script generated via Gemini: {len(script)} chars (verified accurate)")
                    return script
                else:
                    logger.warning(" AI script deviated from prompt, using enhanced fallback")
                    
        except Exception as e:
            logger.warning(f"Gemini script generation failed: {e}")
        
        enhanced_fallback = f"{prompt}. This stunning visual experience showcases the beauty and essence of the scene with cinematic quality and remarkable attention to detail."
        logger.info(f" Using enhanced fallback script: {len(enhanced_fallback)} chars")
        return enhanced_fallback.strip()

    async def generate_tts_audio(self, script: str, filename: str, voice: str = None) -> Optional[str]:
        if not self.edge_tts:
            return None
            
        output_path = f"assets/audio/{filename}.mp3"
        
        voices_to_try = [voice] + self.voices if voice else self.voices
        
        for voice_name in voices_to_try:
            try:
                logger.info(f" Generating audio with voice: {voice_name}")
                communicate = self.edge_tts.Communicate(script, voice_name)
                await communicate.save(output_path)
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                    logger.info(f" Audio generated: {output_path}")
                    return output_path
                    
            except Exception as e:
                logger.warning(f"Voice {voice_name} failed: {e}")
                continue
        
        return None

    def generate_ai_images_google(self, prompt: str, filename_base: str, count: int = 2) -> List[str]:
        images = []
        
        if not self.google_key:
            logger.warning("No Google API key for image generation")
            return images
        
        try:
            image_prompts = [
                f"Create a photorealistic image of exactly this: {prompt}. Include every detail mentioned. Professional photography, perfect lighting, ultra high detail, 8K resolution, sharp focus, accurate colors, award-winning composition.",
                f"Generate a highly accurate photograph showing: {prompt}. Stay true to all specified elements. Cinematic quality, professional studio lighting, crystal clear detail, photographic precision, masterpiece quality."
            ]
            
            for i, img_prompt in enumerate(image_prompts[:count]):
                try:
                    if self.gemini_model:
                        try:
                            response = self.gemini_model.generate_content([
                                f"""Create a HIGHLY DETAILED visual description for AI image generation.

USER'S EXACT REQUIREMENT: "{prompt}"

CRITICAL INSTRUCTIONS:
1. Preserve EVERY detail from the user's prompt (colors, objects, settings, mood, style)
2. Expand with specific visual details WHILE staying 100% faithful to the original
3. Add precise details about:
   - Exact lighting conditions (time of day, light source, shadows)
   - Specific colors and color palette
   - Textures and materials
   - Camera angle and composition
   - Atmosphere and mood
   - Background and foreground elements
4. Use precise, descriptive language for AI accuracy
5. Make it suitable for photorealistic image generation

Write ONLY the detailed visual description, no labels or explanations:"""
                            ], timeout=30)
                        except Exception as e:
                            logger.warning(f"Gemini image API timeout: {e}")
                            continue
                        description = response.text.strip() if response else ""
                        
                        if description:
                            prompt_lower = prompt.lower()
                            desc_lower = description.lower()
                            
                            import re
                            prompt_keywords = set(re.findall(r'\b\w{4,}\b', prompt_lower))
                            desc_keywords = set(re.findall(r'\b\w{4,}\b', desc_lower))
                            
                            overlap = len(prompt_keywords & desc_keywords) / len(prompt_keywords) if prompt_keywords else 0
                            
                            if overlap < 0.6:
                                description = f"{prompt}. {description}"
                                logger.info(f"  Enhanced description with original prompt for accuracy")
                        
                        if self.stability_key and description:
                            image_path = self.generate_stability_image(description, f"{filename_base}_{i}")
                            if image_path:
                                images.append(image_path)
                                logger.info(f"  Image {i+1} generated successfully with accuracy check")
                        
                except Exception as e:
                    logger.warning(f"Image {i+1} generation failed: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Google image generation failed: {e}")
        
        if not images and self.pexels_key:
            images = self.generate_pexels_images(prompt, filename_base, count)
        
        return images

    def generate_stability_image(self, prompt: str, filename: str) -> Optional[str]:
        if not self.stability_key:
            return None
            
        try:
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Authorization": f"Bearer {self.stability_key}",
                "Content-Type": "application/json"
            }
            
            enhanced_prompt = f"{prompt}, highly detailed, professional photography, cinematic lighting, 8K resolution, photorealistic, sharp focus, vivid colors, masterpiece quality"
            
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy, watermark, text, signature, amateur, poor lighting"
            
            data = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1
                    },
                    {
                        "text": negative_prompt,
                        "weight": -1
                    }
                ],
                "cfg_scale": 9,  # Increased for better prompt adherence
                "height": 768,
                "width": 1344,
                "samples": 1,
                "steps": 50,  # Increased steps for better quality
                "sampler": "K_DPM_2_ANCESTRAL"  # Better sampler for photorealistic images
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                for i, artifact in enumerate(result["artifacts"]):
                    if artifact["finishReason"] == "SUCCESS":
                        image_data = base64.b64decode(artifact["base64"])
                        output_path = f"assets/images/{filename}.jpg"
                        
                        with open(output_path, "wb") as f:
                            f.write(image_data)
                        
                        logger.info(f" Stability AI image generated: {output_path}")
                        return output_path
                        
        except Exception as e:
            logger.error(f"Stability AI image generation failed: {e}")
        
        return None

    def generate_pexels_images(self, prompt: str, filename_base: str, count: int = 3) -> List[str]:
        """
        Generate accurate images using Pexels API with intelligent parameter extraction.
        Uses process_prompt_for_pexels to extract both keywords and API parameters for maximum accuracy.
        """
        images = []
        
        if not self.pexels_key:
            return images
        
        try:
            all_photos = []
            
            search_query, pexels_params = process_prompt_for_pexels(prompt)
            
            logger.info(f"  IMAGE SEARCH STRATEGY")
            logger.info(f"    Original: '{prompt[:60]}...'")
            logger.info(f"    Query: '{search_query}'")
            if pexels_params:
                logger.info(f"     Params: {pexels_params}")
            
            logger.info(f" Strategy 1: Smart search with full context...")
            exact_photos = self._search_pexels_photos(search_query, count * 6, extra_params=pexels_params)
            logger.info(f"    Found {len(exact_photos)} photos with smart search")
            all_photos.extend(exact_photos)
            
            if len(all_photos) < count * 3:
                logger.info(" Strategy 2: Key phrase image search...")
                key_phrases = self._extract_image_key_phrases(prompt)
                for phrase in key_phrases[:4]:
                    phrase_photos = self._search_pexels_photos(phrase, count * 4, extra_params=pexels_params)
                    logger.info(f"   Phrase '{phrase}': {len(phrase_photos)} photos")
                    all_photos.extend(phrase_photos)
                    if len(all_photos) >= count * 6:
                        break
            
            if len(all_photos) < count * 2:
                logger.info(" Strategy 3: Primary subject image search...")
                primary = self._extract_primary_subject(prompt)
                if primary:
                    subject_photos = self._search_pexels_photos(primary, count * 4, extra_params=pexels_params)
                    logger.info(f"   Subject '{primary}': {len(subject_photos)} photos")
                    all_photos.extend(subject_photos)
            
            if len(all_photos) < count * 2:
                logger.info(" Strategy 4: Simplified keyword search...")
                simplified = ' '.join(search_query.split()[:2])
                simple_photos = self._search_pexels_photos(simplified, count * 3)
                logger.info(f"   Simplified '{simplified}': {len(simple_photos)} photos")
                all_photos.extend(simple_photos)
            
            seen_ids = set()
            unique_photos = []
            for photo in all_photos:
                photo_id = photo.get('id')
                if photo_id and photo_id not in seen_ids:
                    seen_ids.add(photo_id)
                    unique_photos.append(photo)
            
            unique_photos.sort(key=lambda x: (
                self._calculate_photo_relevance(x, search_query),
                x.get('width', 0) * x.get('height', 0),
                -abs(x.get('width', 1920) / x.get('height', 1080) - 16/9)
            ), reverse=True)
            
            top_photos = unique_photos[:count]
            logger.info(f" Downloading {len(top_photos)} best matching images")
            
            for i, photo in enumerate(top_photos):
                try:
                    img_url = photo['src'].get('large2x') or photo['src'].get('large') or photo['src'].get('original')
                    output_path = f"assets/images/{filename_base}_{i}.jpg"
                    
                    img_response = requests.get(img_url, timeout=20)
                    img_response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        f.write(img_response.content)
                    
                    images.append(output_path)
                    logger.info(f" Pexels image downloaded: {output_path} ({photo.get('width')}x{photo.get('height')})")
                    
                except Exception as e:
                    logger.warning(f"Failed to download Pexels image: {e}")
                        
        except Exception as e:
            logger.error(f"Pexels image generation failed: {e}")
        
        return images
    
    def _search_pexels_photos(self, query: str, max_results: int, extra_params: dict = None) -> List[Dict]:
        """
        Search Pexels for photos with given query and optional extra parameters.
        
        Args:
            query: Search keywords
            max_results: Maximum number of results
            extra_params: Optional dict of Pexels API parameters (orientation, color, size, etc.)
        """
        try:
            headers = {"Authorization": self.pexels_key}
            params = {
                "query": query,
                "per_page": min(max_results, 80),
                "orientation": "landscape",  # Default, can be overridden
                "size": "large"  # Default, can be overridden
            }
            
            if extra_params:
                params.update(extra_params)
            
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get('photos', [])
            
        except Exception as e:
            logger.warning(f"Photo search for '{query}' failed: {e}")
            return []
    
    def _extract_image_key_phrases(self, query: str) -> List[str]:
        """Extract key visual phrases for image search with improved context awareness"""
        import re
        phrases = []
        query_lower = query.lower()
        
        visual_pattern = r'\b(beautiful|stunning|peaceful|majestic|vibrant|serene|dramatic|calm|wild|bright|dark|colorful|golden|crystal|turquoise|cozy|modern|futuristic|vintage|elegant|minimalist|ancient|natural|urban|rural|tropical|arctic|sunny|rainy|cloudy|foggy|misty)\s+(\w+(?:\s+\w+)?)\b'
        matches = re.findall(visual_pattern, query_lower)
        for adj, noun in matches:
            phrases.append(f"{adj} {noun.strip()}")
        
        noun_phrase_pattern = r'\b(\w+)\s+(landscape|scenery|view|scene|environment|atmosphere|setting|background|location)\b'
        noun_matches = re.findall(noun_phrase_pattern, query_lower)
        for modifier, noun in noun_matches:
            if modifier not in ['the', 'a', 'an', 'of', 'in', 'at', 'on']:
                phrases.append(f"{modifier} {noun}")
        
        visual_subjects = [
            'sunset', 'sunrise', 'ocean', 'sea', 'beach', 'mountain', 'forest',
            'city', 'street', 'building', 'waterfall', 'river', 'lake', 'desert',
            'garden', 'park', 'tree', 'flower', 'sky', 'cloud', 'coffee', 'food',
            'architecture', 'landscape', 'nature', 'interior', 'room', 'office',
            'cafe', 'restaurant', 'shop', 'technology', 'computer', 'phone',
            'mountains', 'beaches', 'forests', 'cities', 'buildings', 'waterfalls',
            'animals', 'wildlife', 'birds', 'fish', 'underwater', 'space', 'galaxy',
            'stars', 'planets', 'aurora', 'northern lights', 'volcano', 'cave',
            'canyon', 'valley', 'meadow', 'field', 'countryside', 'village'
        ]
        
        found_subjects = [subject for subject in visual_subjects if subject in query_lower]
        phrases.extend(found_subjects[:4])
        
        words = query_lower.split()
        if len(words) >= 2:
            for i in range(len(words) - 1):
                if words[i] not in ['a', 'an', 'the', 'of', 'in', 'at', 'on', 'with', 'for'] and len(words[i]) > 3:
                    two_word_phrase = f"{words[i]} {words[i+1]}"
                    if two_word_phrase not in phrases and len(phrases) < 10:
                        phrases.append(two_word_phrase)
        
        return phrases[:8]
    
    def _calculate_photo_relevance(self, photo: Dict, query: str) -> float:
        """
        Calculate relevance score for a photo based on the search query.
        Higher score means better match.
        """
        score = 0.0
        query_lower = query.lower()
        
        width = photo.get('width', 0)
        height = photo.get('height', 0)
        
        if width >= 3840 and height >= 2160:
            score += 3.0
        elif width >= 1920 and height >= 1080:
            score += 2.0
        elif width >= 1280 and height >= 720:
            score += 1.0
        
        aspect_ratio = width / height if height > 0 else 0
        ideal_ratio = 16 / 9
        aspect_diff = abs(aspect_ratio - ideal_ratio)
        if aspect_diff < 0.1:
            score += 2.0
        elif aspect_diff < 0.3:
            score += 1.0
        
        avg_color = photo.get('avg_color', '')
        if avg_color:
            if 'dark' in query_lower or 'night' in query_lower:
                r, g, b = int(avg_color[1:3], 16), int(avg_color[3:5], 16), int(avg_color[5:7], 16)
                if (r + g + b) / 3 < 100:
                    score += 1.5
            elif 'bright' in query_lower or 'day' in query_lower or 'sunny' in query_lower:
                r, g, b = int(avg_color[1:3], 16), int(avg_color[3:5], 16), int(avg_color[5:7], 16)
                if (r + g + b) / 3 > 150:
                    score += 1.5
        
        return score
    
    def _extract_primary_subject(self, query: str) -> Optional[str]:
        """Extract the primary subject from a query with better accuracy"""
        query_lower = query.lower()
        
        priority_subjects = [
            'virtual reality', 'northern lights', 'milky way', 'solar system',
            'coral reef', 'tropical rainforest', 'volcanic eruption', 'sand dunes'
        ]
        
        for subject in priority_subjects:
            if subject in query_lower:
                return subject
        
        subjects = [
            'coffee', 'ocean', 'mountain', 'beach', 'forest', 'city', 'sunset',
            'sunrise', 'building', 'waterfall', 'lake', 'river', 'desert', 'garden',
            'flower', 'tree', 'sky', 'cloud', 'people', 'person', 'food', 'technology',
            'vr', 'headset', 'robot', 'ai', 'space', 'galaxy', 'stars', 'planets',
            'volcano', 'cave', 'canyon', 'valley', 'meadow', 'field', 'countryside',
            'village', 'town', 'architecture', 'landscape', 'nature', 'wildlife',
            'animals', 'birds', 'underwater', 'aurora', 'mountains', 'beaches',
            'forests', 'cities', 'buildings', 'waterfalls', 'rivers', 'lakes'
        ]
        
        for subject in subjects:
            if subject in query_lower:
                return subject
        
        words = query_lower.split()
        if len(words) > 0:
            return words[0]
        
        return None

    def generate_ai_video_replicate(self, prompt: str, filename: str, duration: int = 3) -> Optional[str]:
        if not self.replicate_client:
            logger.warning("Replicate client not available")
            return None
            
        try:
            logger.info(" Generating AI video with Replicate...")
            logger.info(f" Prompt: '{prompt}', Duration: {duration}s")
            
            enhanced_prompt = f"{prompt}, cinematic, high quality, smooth motion, professional"
            
            model = "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351"
            
            try:
                logger.info(" Running Replicate Zeroscope model...")
                
                num_frames = duration * 8
                
                output = self.replicate_client.run(
                    model,
                    input={
                        "prompt": enhanced_prompt,
                        "batch_size": 1,
                        "num_frames": num_frames,
                        "num_inference_steps": 50,
                        "guidance_scale": 17.5,
                        "width": 1024,
                        "height": 576,
                        "fps": 24,
                        "remove_watermark": False
                    }
                )
                
                if output:
                    if isinstance(output, str):
                        video_url = output
                    elif isinstance(output, list) and output:
                        video_url = output[0]
                    else:
                        logger.error(" No video URL in output")
                        return None
                    
                    output_path = f"assets/videos/{filename}.mp4"
                    
                    logger.info(f" Downloading AI-generated video...")
                    video_response = requests.get(video_url, stream=True, timeout=120)
                    video_response.raise_for_status()
                    
                    with open(output_path, 'wb') as f:
                        for chunk in video_response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        file_size = os.path.getsize(output_path) / (1024 * 1024)
                        logger.info(f" AI video generated: {output_path} ({file_size:.1f} MB)")
                        return output_path
                    else:
                        logger.error(" Generated file too small or missing")
                        return None
                        
            except Exception as e:
                logger.error(f" Replicate video generation failed: {e}")
                return None
                    
        except Exception as e:
            logger.error(f" Replicate setup failed: {e}")
            return None

    def generate_ai_video_runway(self, prompt: str, filename: str) -> Optional[str]:
        if not self.runway_key:
            logger.warning("Runway API key not available")
            return None
            
        try:
            logger.info(" Generating AI video with Runway ML...")
            
            url = "https://api.runwayml.com/v1/generate"
            
            headers = {
                "Authorization": f"Bearer {self.runway_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gen2",
                "prompt": f"Cinematic video: {prompt}",
                "duration": 4,
                "resolution": "1280x768",
                "seed": None
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=180)
            
            if response.status_code == 200:
                result = response.json()
                
                if "video_url" in result:
                    video_url = result["video_url"]
                    output_path = f"assets/videos/{filename}.mp4"
                    
                    video_response = requests.get(video_url, timeout=120)
                    with open(output_path, 'wb') as f:
                        f.write(video_response.content)
                    
                    logger.info(f" Runway AI video generated: {output_path}")
                    return output_path
                    
        except Exception as e:
            logger.error(f"Runway video generation failed: {e}")
        
        return None

    def generate_pexels_video(self, prompt: str, filename: str, duration: int = 10) -> Optional[str]:
        if not self.pexels_video_generator:
            logger.warning("Pexels Video Generator not available")
            return None
            
        try:
            logger.info(f" Generating video with Pexels API for: '{prompt}'")
            
            compilation_path = self.pexels_video_generator.generate_video_compilation(
                prompt=prompt,  # Use exact user prompt
                duration=duration,
                num_clips=3
            )
            
            if compilation_path:
                import shutil
                final_path = f"assets/videos/{filename}.mp4"
                shutil.move(compilation_path, final_path)
                logger.info(f" Pexels video compilation generated: {final_path}")
                return final_path
            
            logger.info(" Falling back to Pexels slideshow...")
            slideshow_path = self.pexels_video_generator.generate_slideshow_video(
                prompt=prompt,  # Use exact user prompt
                duration=duration
            )
            
            if slideshow_path:
                import shutil
                final_path = f"assets/videos/{filename}.mp4"
                shutil.move(slideshow_path, final_path)
                logger.info(f" Pexels slideshow generated: {final_path}")
                return final_path
                
        except Exception as e:
            logger.error(f"Pexels video generation failed: {e}")
            
        return None

    def generate_video_from_images(self, images: List[str], filename: str, audio_path: Optional[str] = None) -> Optional[str]:
        if not images:
            return None
            
        try:
            try:
                from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
            except ImportError:
                logger.error("MoviePy not installed. Install with: pip install moviepy")
                return None
            
            clips = []
            for img_path in images:
                if os.path.exists(img_path):
                    clip = ImageClip(img_path).with_duration(3)
                    clip = clip.resized(width=1280)
                    clips.append(clip)
            
            if clips:
                final_video = concatenate_videoclips(clips, method="compose")
                
                if audio_path and os.path.exists(audio_path):
                    audio = AudioFileClip(audio_path)
                    if audio.duration < final_video.duration:
                        audio = audio.with_effects([audio.fx.audio_loop(duration=final_video.duration)])
                    elif audio.duration > final_video.duration:
                        audio = audio.subclipped(0, final_video.duration)
                    
                    final_video = final_video.with_audio(audio)
                
                output_path = f"assets/videos/{filename}.mp4"
                final_video.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    fps=24,
                    logger=None
                )
                
                for clip in clips:
                    clip.close()
                if audio_path:
                    audio.close()
                final_video.close()
                
                logger.info(f" Cinematic video created: {output_path}")
                return output_path
                
        except Exception as e:
            logger.error(f"Video creation from images failed: {e}")
        
        return None

    def generate_complete_media(self, prompt: str) -> Dict[str, Any]:
        start_time = time.time()
        timestamp = int(time.time())
        
        logger.info(f" Generating AI media for: '{prompt}'")
        
        results = {
            'success': False,
            'prompt': prompt,
            'script': None,
            'script_file': None,
            'audio': None,
            'images': [],
            'video': None,
            'generation_time': 0,
            'components': {
                'script': False,
                'audio': False,
                'images': False,
                'video': False
            },
            'ai_generated': True
        }
        
        try:
            logger.info(" Generating AI script...")
            try:
                script_text = self.generate_enhanced_script(prompt)
            except Exception as e:
                logger.warning(f"Script generation failed fast: {e}")
                script_text = ""
            results['script'] = script_text
            
            script_path = f"assets/scripts/ai_generated_{timestamp}.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(f"AI Generated Script for: {prompt}\n\n{script_text}")
            
            results['script_file'] = script_path
            results['components']['script'] = True
            logger.info(f" AI script saved: {script_path}")
            
            logger.info(" Generating AI audio...")
            try:
                audio_path = asyncio.run(self.generate_tts_audio(script_text, f"ai_audio_{timestamp}"))
            except Exception as e:
                logger.warning(f"Audio generation failed fast: {e}")
                audio_path = None
            if audio_path:
                results['audio'] = audio_path
                results['components']['audio'] = True
                logger.info(f" AI audio ready: {audio_path}")
            
            logger.info(" Generating AI images...")
            try:
                images = self.generate_ai_images_google(prompt, f"ai_image_{timestamp}", count=2)
            except Exception as e:
                logger.warning(f"Image generation failed fast: {e}")
                images = []
            if images:
                results['images'] = images
                results['components']['images'] = True
                logger.info(f" Generated {len(images)} AI images")
            
            logger.info(" Generating AI video...")
            video_path = None
            
            if self.pexels_video_generator:
                video_path = self.generate_pexels_video(prompt, f"ai_video_{timestamp}", duration=10)
            
            if not video_path and self.replicate_client:
                video_path = self.generate_ai_video_replicate(prompt, f"ai_video_{timestamp}")
            if not video_path and self.runway_key:
                video_path = self.generate_ai_video_runway(prompt, f"ai_video_{timestamp}")
                
            if not video_path and images:
                video_path = self.generate_video_from_images(images, f"ai_video_{timestamp}", audio_path)
                
            if not video_path:
                logger.info(" Attempting fallback: prompt-to-video only")
                if self.replicate_client:
                    video_path = self.generate_ai_video_replicate(prompt, f"ai_video_{timestamp}_fallback")
                elif self.runway_key:
                    video_path = self.generate_ai_video_runway(prompt, f"ai_video_{timestamp}_fallback")
            if video_path:
                results['video'] = video_path
                results['components']['video'] = True
                logger.info(f" AI video ready: {video_path}")
            
            results['generation_time'] = time.time() - start_time
            
            successful_components = sum(results['components'].values())
            if successful_components >= 3:
                results['success'] = True
                logger.info(f" AI media generation completed! ({successful_components}/4 components)")
            else:
                results['success'] = False
                logger.warning(" Not enough AI components generated")
            
        except Exception as e:
            logger.error(f" AI media generation failed: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results

    def generate_complete_media_with_options(self, prompt: str, video_method: str = "Pexels Stock Videos (Recommended)", video_duration: int = 10) -> Dict[str, Any]:
        logger.info(f" Generating AI media for: '{prompt}'")
        logger.info(f" Video method: {video_method}, Duration: {video_duration}s")
        
        timestamp = int(time.time())
        start_time = time.time()
        
        results = {
            'success': False,
            'script': '',
            'audio': None,
            'images': [],
            'video': None,
            'script_file': None,
            'generation_time': 0,
            'components': {
                'script': False,
                'audio': False,
                'images': False,
                'video': False
            },
            'ai_generated': True,
            'video_method': video_method
        }
        
        try:
            logger.info(" Generating AI script...")
            try:
                script_text = self.generate_enhanced_script(prompt)
            except Exception as e:
                logger.warning(f"Script generation failed: {e}")
                script_text = f"A captivating story about {prompt}"
            
            results['script'] = script_text
            
            script_path = f"assets/scripts/ai_generated_{timestamp}.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(f"AI Generated Script for: {prompt}\n\n{script_text}")
            
            results['script_file'] = script_path
            results['components']['script'] = True
            logger.info(f" AI script saved: {script_path}")
            
            logger.info(f" Generating video using: {video_method}")
            video_path = None
            
            import concurrent.futures
            from functools import partial
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                
                if "Cinematic" in video_method or "Pexels" in video_method:
                    if self.pexels_video_generator:
                        video_future = executor.submit(self.generate_pexels_video, prompt, f"ai_video_{timestamp}", video_duration)
                        futures['video'] = video_future
                elif "AI Generated" in video_method:
                    if self.replicate_client:
                        video_future = executor.submit(self.generate_ai_video_replicate, prompt, f"ai_video_{timestamp}", video_duration)
                        futures['video'] = video_future
                
                audio_future = executor.submit(lambda: asyncio.run(self.generate_tts_audio(script_text, f"ai_audio_{timestamp}")))
                futures['audio'] = audio_future
                
                images_future = executor.submit(self.generate_pexels_images, prompt, f"ai_image_{timestamp}", 3)
                futures['images'] = images_future
                
                try:
                    audio_path = futures['audio'].result(timeout=30)  # 30 sec timeout for audio
                except Exception as e:
                    logger.warning(f"Audio generation failed: {e}")
                    audio_path = None
                
                try:
                    images = futures['images'].result(timeout=20)
                except Exception as e:
                    logger.warning(f"Image generation failed: {e}")
                    images = []
                
                if 'video' in futures:
                    try:
                        timeout_seconds = max(600, video_duration * 30)
                        logger.info(f" Waiting for video compilation (timeout: {timeout_seconds}s)...")
                        video_path = futures['video'].result(timeout=timeout_seconds)
                    except Exception as e:
                        logger.warning(f"Video generation failed: {e}")
                        video_path = None
            
            if audio_path:
                results['audio'] = audio_path
                results['components']['audio'] = True
                logger.info(f" AI audio ready: {audio_path}")
            
            if images:
                results['images'] = images
                results['components']['images'] = True
                logger.info(f" Generated {len(images)} AI images")
            
            if not video_path:
                logger.info(" Primary method failed, trying fallback...")
                
                if "AI Generated" in video_method and self.pexels_video_generator:
                    logger.info(" AI generation failed - using Cinematic Library fallback...")
                    video_path = self.generate_pexels_video(prompt, f"ai_video_{timestamp}_fallback", duration=video_duration)
                
                if not video_path and images:
                    logger.info(" Creating video from images...")
                    video_path = self.generate_video_from_images(images, f"ai_video_{timestamp}_fallback", audio_path)
            
            if video_path:
                results['video'] = video_path
                results['components']['video'] = True
                logger.info(f" AI video ready: {video_path}")
            
            results['generation_time'] = time.time() - start_time
            
            successful_components = sum(results['components'].values())
            if successful_components >= 3:
                results['success'] = True
                logger.info(f" AI media generation completed in {results['generation_time']:.1f}s! ({successful_components}/4 components)")
            else:
                results['success'] = False
                logger.warning(" Not enough AI components generated")
        
        except Exception as e:
            logger.error(f"Media generation error: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results
    
    def generate_complete_media_with_selected_video(self, prompt: str, selected_video: Dict = None, video_duration: int = 10) -> Dict[str, Any]:
        """
        Generate complete media using a pre-selected video from human-in-the-loop selection.
        
        Args:
            prompt: User's text prompt
            selected_video: Pre-selected video dict with 'url', 'thumbnail', 'id', etc.
            video_duration: Duration for the final video
        """
        logger.info(f" Generating AI media with user-selected video for: '{prompt}'")
        
        timestamp = int(time.time())
        start_time = time.time()
        
        results = {
            'success': False,
            'script': '',
            'audio': None,
            'images': [],
            'video': None,
            'script_file': None,
            'generation_time': 0,
            'components': {
                'script': False,
                'audio': False,
                'images': False,
                'video': False
            },
            'selected_video_info': selected_video
        }
        
        try:
            logger.info(" Generating AI script...")
            try:
                script_text = self.generate_enhanced_script(prompt)
            except Exception as e:
                logger.warning(f"Script generation failed: {e}")
                script_text = f"A captivating story about {prompt}"
            
            results['script'] = script_text
            
            script_path = f"assets/scripts/ai_generated_{timestamp}.txt"
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(f"AI Generated Script for: {prompt}\n\n{script_text}")
            
            results['script_file'] = script_path
            results['components']['script'] = True
            logger.info(f" AI script saved: {script_path}")
            
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = {}
                
                audio_future = executor.submit(lambda: asyncio.run(self.generate_tts_audio(script_text, f"ai_audio_{timestamp}")))
                futures['audio'] = audio_future
                
                images_future = executor.submit(self.generate_pexels_images, prompt, f"ai_image_{timestamp}", 3)
                futures['images'] = images_future
                
                if selected_video and self.pexels_video_generator:
                    logger.info(f" Using selected video: ID {selected_video.get('id')}")
                    video_future = executor.submit(
                        self.pexels_video_generator.download_video,
                        selected_video,
                        f"selected_video_{timestamp}"
                    )
                    futures['video'] = video_future
                
                try:
                    audio_path = futures['audio'].result(timeout=30)
                except Exception as e:
                    logger.warning(f"Audio generation failed: {e}")
                    audio_path = None
                
                try:
                    images = futures['images'].result(timeout=20)
                except Exception as e:
                    logger.warning(f"Image generation failed: {e}")
                    images = []
                
                video_path = None
                if 'video' in futures:
                    try:
                        logger.info(f" Downloading selected video...")
                        video_path = futures['video'].result(timeout=60)
                    except Exception as e:
                        logger.warning(f"Video download failed: {e}")
                        video_path = None
            
            if audio_path and os.path.exists(audio_path):
                results['audio'] = audio_path
                results['components']['audio'] = True
                logger.info(f" Audio: {audio_path}")
            
            if images:
                results['images'] = images
                results['components']['images'] = True
                logger.info(f" Images: {len(images)} generated")
            
            if video_path and os.path.exists(video_path):
                results['video'] = video_path
                results['components']['video'] = True
                logger.info(f" Selected video: {video_path}")
            
            results['generation_time'] = time.time() - start_time
            
            successful_components = sum(results['components'].values())
            if successful_components >= 3:
                results['success'] = True
                logger.info(f" Media generation with selected video completed in {results['generation_time']:.1f}s! ({successful_components}/4 components)")
            else:
                results['success'] = False
                logger.warning(" Not enough components generated")
        
        except Exception as e:
            logger.error(f"Media generation error: {e}")
            results['success'] = False
            results['error'] = str(e)
        
        return results

StreamlinedMediaGenerator = AdvancedAIMediaGenerator
EnhancedStreamlinedMediaGenerator = AdvancedAIMediaGenerator

def main():
    generator = AdvancedAIMediaGenerator()
    
    test_prompt = "A magical fairy tale castle floating in the clouds at sunset"
    
    print(f"\n Testing AI Media Generator")
    print(f"Prompt: '{test_prompt}'")
    print("=" * 70)
    
    results = generator.generate_complete_media(test_prompt)
    
    print(f"\n RESULTS:")
    print(f"Success: {'' if results['success'] else ''} {results['success']}")
    print(f"AI Generated: {'' if results.get('ai_generated') else ''}")
    print(f"Time: {results['generation_time']:.2f}s")
    print()
    
    components = results.get('components', {})
    print(" SCRIPT:", "" if components.get('script') else "")
    print(" AUDIO:", "" if components.get('audio') else "")
    print(" IMAGES:", f" {len(results.get('images', []))}" if components.get('images') else "")
    print(" VIDEO:", "" if components.get('video') else "")

if __name__ == "__main__":
    main()
