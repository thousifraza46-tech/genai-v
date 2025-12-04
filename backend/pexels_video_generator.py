
import os
import requests
import time
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_keywords_for_pexels(user_prompt: str, max_keywords: int = 6) -> str:
    """
    Extract clean keywords from user prompt for Pexels API search.
    
    Args:
        user_prompt: The full user input prompt
        max_keywords: Maximum number of keywords to return (default: 6)
    
    Returns:
        Clean keyword string suitable for Pexels search
    """
    # Try NLTK if available, otherwise use simple fallback
    try:
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            stop_words = set(stopwords.words('english'))
        
        text_lower = user_prompt.lower()
        
        important_modifiers = {
            'beautiful', 'stunning', 'peaceful', 'majestic', 'vibrant', 'serene', 'dramatic',
            'calm', 'wild', 'bright', 'dark', 'colorful', 'golden', 'crystal', 'turquoise',
            'cozy', 'modern', 'futuristic', 'vintage', 'elegant', 'minimalist', 'rustic',
            'tropical', 'ancient', 'historic', 'contemporary', 'luxurious', 'charming',
            'sunset', 'sunrise', 'night', 'day', 'morning', 'evening', 'aerial', 'close-up',
            'slow', 'fast', 'cinematic', 'natural', 'urban', 'rural', 'underwater', 'timelapse'
        }
        
        try:
            words = word_tokenize(text_lower)
        except LookupError:
            nltk.download('punkt', quiet=True)
            words = word_tokenize(text_lower)
        
        keywords = []
        for word in words:
            if word.isalpha() and len(word) > 2:
                if word in important_modifiers or word not in stop_words:
                    keywords.append(word)
        
        important_keywords = keywords[:max_keywords]
        
        keyword_string = ' '.join(important_keywords)
        
        logger.info(f" Extracted keywords: '{user_prompt}' -> '{keyword_string}'")
        
        return keyword_string if keyword_string else user_prompt
        
    except ImportError:
        # NLTK not available - use simple fallback keyword extraction
        logger.info("NLTK not available, using simple keyword extraction")
        
        # Simple stopwords list
        stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 
                     'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 
                     'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 
                     'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 
                     'your', 'his', 'her', 'its', 'our', 'their'}
        
        # Extract words (simple split)
        words = user_prompt.lower().split()
        keywords = [w.strip('.,!?;:') for w in words 
                   if len(w) > 2 and w.lower() not in stop_words][:max_keywords]
        
        keyword_string = ' '.join(keywords)
        logger.info(f" Extracted keywords (simple): '{user_prompt}' -> '{keyword_string}'")
        
        return keyword_string if keyword_string else user_prompt
        
    except Exception as e:
        logger.warning(f"Keyword extraction failed: {e}, using original prompt")
        return user_prompt

def get_fast_video_link(video_files: List[dict]) -> Optional[str]:
    """
    Select the fastest-loading video link from Pexels video_files list.
    
    Priority:
    1. Find first video with quality == 'sd' (standard definition, faster)
    2. If no SD found, return the last video in list (usually smallest)
    
    Args:
        video_files: List of video file dictionaries from Pexels API
    
    Returns:
        Video link string, or None if list is empty
    """
    if not video_files:
        return None
    
    for video_file in video_files:
        quality = video_file.get('quality')
        if quality and quality.lower() == 'sd' and video_file.get('link'):
            logger.info(f" Selected SD quality video for faster loading")
            return video_file['link']
    
    last_video = video_files[-1]
    if last_video.get('link'):
        logger.info(f" Selected smallest video file for faster loading")
        return last_video['link']
    
    return None

def process_prompt_for_pexels(user_prompt: str) -> tuple:
    """
    Process user prompt to extract both Pexels API parameters and clean search keywords.
    
    This function:
    1. Analyzes prompt for Pexels API filter parameters (orientation, color, size)
    2. Extracts clean keywords using NLTK (removes only basic stopwords, keeps visual descriptors)
    3. Returns optimized search query and parameters for Pexels API
    
    Args:
        user_prompt: Full user input prompt (e.g., "A tall, high-quality video of a building in black and white")
    
    Returns:
        tuple: (search_query: str, params: dict)
        - search_query: Clean keywords for search (e.g., "modern building cityscape")
        - params: Pexels API parameters (e.g., {'orientation': 'portrait', 'size': 'large', 'color': 'black'})
    
    Example:
        >>> process_prompt_for_pexels("A tall, high-quality video of a building in black and white")
        ("modern building architecture", {'orientation': 'portrait', 'size': 'large', 'color': 'black'})
    """
    params = {}
    text_lower = user_prompt.lower()
    
    parameter_words = set()
    
    orientation_portrait = ['tall', 'vertical', 'standing', 'portrait', 'upright']
    orientation_landscape = ['wide', 'landscape', 'horizontal', 'panoramic', 'widescreen']
    
    for word in orientation_portrait:
        if word in text_lower:
            params['orientation'] = 'portrait'
            parameter_words.add(word)
            break
    
    if 'orientation' not in params:
        for word in orientation_landscape:
            if word in text_lower:
                params['orientation'] = 'landscape'
                parameter_words.add(word)
                break
    
    if 'black and white' in text_lower or 'monochrome' in text_lower or 'grayscale' in text_lower:
        params['color'] = 'black'
        parameter_words.update(['monochrome', 'grayscale'])
    
    quality_keywords = ['hd', 'high quality', 'high-quality', '4k', 'ultra hd', 'high resolution', 'high-resolution']
    for keyword in quality_keywords:
        if keyword in text_lower:
            params['size'] = 'large'
            parameter_words.update(['hd', '4k', 'ultra', 'quality', 'resolution'])
            break
    
    try:
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            stop_words = set(stopwords.words('english'))
        
        visual_descriptors = {
            'beautiful', 'stunning', 'peaceful', 'majestic', 'vibrant', 'serene', 'dramatic',
            'calm', 'wild', 'bright', 'dark', 'colorful', 'golden', 'crystal', 'turquoise',
            'cozy', 'modern', 'futuristic', 'vintage', 'elegant', 'minimalist', 'rustic',
            'tropical', 'ancient', 'historic', 'contemporary', 'luxurious', 'charming',
            'graceful', 'brilliant', 'misty', 'foggy', 'sunny', 'cloudy', 'starry',
            'clear', 'sandy', 'rocky', 'green', 'blue', 'red', 'white', 'black',
            'purple', 'pink', 'orange', 'yellow', 'sunset', 'sunrise', 'twilight',
            'night', 'day', 'morning', 'evening', 'autumn', 'winter', 'spring', 'summer'
        }
        
        try:
            words = word_tokenize(text_lower)
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
            words = word_tokenize(text_lower)
        
        keywords = []
        for word in words:
            if word.isalpha() and len(word) > 2:
                if (word in visual_descriptors or 
                    (word not in stop_words and word not in parameter_words)):
                    keywords.append(word)
        
        search_query = ' '.join(keywords[:12])
        
        if not search_query:
            basic_stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'is', 'are', 'was', 'were'}
            search_query = ' '.join([w for w in words if w.isalpha() and w not in basic_stopwords][:12])
        
        logger.info(f" Processed prompt: '{user_prompt[:60]}...'")
        logger.info(f"    Query: '{search_query}'")
        if params:
            logger.info(f"     Params: {params}")
        
    except Exception as e:
        logger.warning(f" NLTK processing failed: {e}, using simplified extraction")
        words = text_lower.split()
        basic_stopwords = {'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'is', 'are', 'was', 'were'}
        keywords = [w.strip('.,!?;:') for w in words 
                   if w not in parameter_words and w not in basic_stopwords and len(w) > 2]
        search_query = ' '.join(keywords[:10])
    
    if not search_query.strip():
        search_query = user_prompt
    
    return search_query, params

class PexelsVideoGenerator:
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or self._get_api_key()
        if not self.api_key:
            logger.warning(" No Pexels API key found. Video generation will be limited.")
            
        self.base_url = "https://api.pexels.com"
        self.headers = {"Authorization": self.api_key} if self.api_key else {}
        
        os.makedirs("assets/videos", exist_ok=True)
        os.makedirs("assets/images", exist_ok=True)
        
        try:
            from intelligent_trainer import get_trainer
            self.trainer = get_trainer()
            logger.info(" Intelligent trainer initialized")
        except Exception as e:
            logger.warning(f"Intelligent trainer not available: {e}")
            self.trainer = None
        
        try:
            from smart_learner import VideoGenerationLearner
            self.learner = VideoGenerationLearner()
            logger.info(" Smart learning system initialized")
        except Exception as e:
            logger.warning(f"Learning system not available: {e}")
            self.learner = None
        
    def _get_api_key(self) -> Optional[str]:
        try:
            from config import PEXELS_API_KEY
            return PEXELS_API_KEY
        except ImportError:
            return os.getenv("PEXELS_API_KEY")
    
    def search_videos(self, query: str, count: int = 5, min_duration: int = 3) -> List[Dict]:
        """
        Search for videos on Pexels with intelligent parameter extraction and keyword optimization.
        Uses process_prompt_for_pexels to extract both search query and API parameters.
        """
        if not self.api_key:
            logger.warning("No Pexels API key available")
            return []
            
        try:
            logger.info(f" Searching Pexels videos for: '{query}'")
            
            search_query, pexels_params = process_prompt_for_pexels(query)
            
            enhanced_query = search_query
            recommendations = {}
            
            if self.learner:
                logger.info(" Analyzing prompt with learning system...")
                analysis = self.learner.analyze_prompt(query)
                
                suggestions = self.learner.suggest_improvements(query)
                if suggestions:
                    logger.info(f" Suggestion: {suggestions[0]}")
                
                similar = self.learner.get_similar_prompts(query, limit=3)
                if similar:
                    logger.info(f" Found {len(similar)} similar successful prompts in history")
                
                recommendations = analysis["recommendations"]
                
                if "min_duration" in recommendations:
                    min_duration = max(min_duration, recommendations["min_duration"])
            
            all_videos = []
            search_query_used = enhanced_query
            
            logger.info(f" Strategy 1: Primary search with full context '{enhanced_query}'...")
            exact_videos = self._search_with_query(enhanced_query, count * 3, min_duration, extra_params=pexels_params)
            logger.info(f"    Found {len(exact_videos)} videos with primary search")
            all_videos.extend(exact_videos)
            
            if len(all_videos) < count:
                logger.info(f" Strategy 2: Key phrase search (detailed context)...")
                key_phrases = self._extract_key_phrases(query)
                for phrase in key_phrases[:3]:
                    phrase_videos = self._search_with_query(phrase, count * 2, min_duration)
                    logger.info(f"   Phrase '{phrase}': {len(phrase_videos)} videos")
                    all_videos.extend(phrase_videos)
                    search_query_used = phrase
                    if len(all_videos) >= count * 3:
                        break
            
            if len(all_videos) < count:
                logger.info(f" Strategy 3: Primary subject search (core topic)...")
                primary = self._extract_primary_subject(query)
                if primary:
                    subject_videos = self._search_with_query(primary, count * 2, min_duration)
                    logger.info(f"   Subject '{primary}': {len(subject_videos)} videos")
                    all_videos.extend(subject_videos)
                    search_query_used = primary
            
            if len(all_videos) < count:
                logger.info(f" Strategy 4: Broader search with simplified keywords...")
                simplified = ' '.join(enhanced_query.split()[:3])
                broader_videos = self._search_with_query(simplified, count * 2, min_duration)
                logger.info(f"   Simplified '{simplified}': {len(broader_videos)} videos")
                all_videos.extend(broader_videos)
            
            seen_ids = set()
            unique_videos = []
            for video in all_videos:
                if video['id'] not in seen_ids:
                    seen_ids.add(video['id'])
                    unique_videos.append(video)
            
            unique_videos.sort(key=lambda x: (
                self._calculate_relevance_score(x, enhanced_query),
                x.get('width', 0) * x.get('height', 0),
                x.get('duration', 0)
            ), reverse=True)
            
            top_videos = unique_videos[:count]
            
            if self.learner:
                quality = top_videos[0].get('quality', 'hd') if top_videos else 'sd'
                success = len(top_videos) >= count
                self.learner.record_generation(
                    prompt=query,
                    search_query=search_query_used,
                    videos_found=len(top_videos),
                    video_quality=quality,
                    success=success
                )
                logger.info(" Recorded search results for learning")
            
            logger.info(f" Returning {len(top_videos)} best matching videos")
            if top_videos:
                logger.info(f" Top video: {top_videos[0].get('width')}x{top_videos[0].get('height')}, {top_videos[0].get('duration')}s")
            
            return top_videos
            
        except Exception as e:
            logger.error(f" Pexels video search failed: {e}")
            
            if self.learner:
                self.learner.record_generation(
                    prompt=query,
                    search_query=query,
                    videos_found=0,
                    success=False
                )
            
            return []
    
    def search_videos_for_selection(self, query: str, count: int = 10, min_duration: int = 3) -> List[Dict]:
        """
        Search for multiple videos for human-in-the-loop selection.
        Returns a list of videos with thumbnails for user to choose from.
        
        Args:
            query: Search query from user
            count: Number of videos to return (default 10)
            min_duration: Minimum video duration in seconds
            
        Returns:
            List of video dictionaries with thumbnails for selection
        """
        if not self.api_key:
            logger.warning("No Pexels API key available")
            return []
            
        try:
            logger.info(f" Fetching {count} videos for user selection: '{query}'")
            
            search_query, pexels_params = process_prompt_for_pexels(query)
            logger.info(f" Processed search: '{search_query}' with params {pexels_params}")
            
            videos = self._search_with_query(search_query, count, min_duration, extra_params=pexels_params)
            
            logger.info(f" Found {len(videos)} videos for selection")
            return videos
            
        except Exception as e:
            logger.error(f" Failed to fetch videos for selection: {e}")
            return []
    
    def _search_with_query(self, search_query: str, max_results: int, min_duration: int, extra_params: dict = None) -> List[Dict]:
        """
        Perform a single search with the given query and optional extra parameters.
        
        Args:
            search_query: The search keywords
            max_results: Maximum number of results to return
            min_duration: Minimum video duration in seconds
            extra_params: Optional dict of Pexels API parameters (orientation, color, size, etc.)
        """
        try:
            url = f"{self.base_url}/videos/search"
            params = {
                "query": search_query,
                "per_page": min(max_results, 80),  # Changed from 1 to support up to 80 results
                "orientation": "landscape",  # Default, can be overridden
                "size": "medium"  # Default, can be overridden
            }
            
            if extra_params:
                params.update(extra_params)
            
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for video in data.get("videos", []):
                video_info = self._extract_video_info(video, min_duration)
                if video_info:
                    videos.append(video_info)
            
            return videos
            
        except Exception as e:
            logger.error(f"Search with query '{search_query}' failed: {e}")
            return []
    
    def _extract_key_phrases(self, query: str) -> List[str]:
        """
        Extract 3-5 most important descriptive phrases from the query.
        These should capture the essence of what the user wants.
        """
        import re
        
        phrases = []
        query_lower = query.lower()
        
        adjective_noun_pattern = r'\b(beautiful|stunning|peaceful|majestic|vibrant|serene|dramatic|calm|wild|busy|quiet|bright|dark|colorful|golden|crystal|turquoise|snow-covered|sun-lit|moonlit|misty|foggy|cloudy|starry|aerial|cinematic|slow|fast|timelapse|underwater|natural|urban|rural|modern|ancient|tropical|arctic)\s+(\w+)\b'
        matches = re.findall(adjective_noun_pattern, query_lower)
        for adj, noun in matches:
            phrases.append(f"{adj} {noun}")
        
        compound_phrases = [
            'sunset over ocean', 'sunrise over mountain', 'waves crashing', 'waterfall flowing',
            'city lights', 'night sky', 'starry night', 'full moon', 'golden hour',
            'blue sky', 'white clouds', 'green forest', 'snowy mountain', 'sandy beach',
            'busy street', 'quiet lake', 'flowing river', 'falling snow', 'heavy rain',
            'lightning storm', 'fire burning', 'traffic moving', 'people walking',
            'birds flying', 'fish swimming', 'flowers blooming', 'trees swaying',
            'wind blowing', 'sun setting', 'moon rising', 'clouds moving',
            'aerial view', 'drone shot', 'close up', 'wide angle', 'slow motion',
            'time lapse', 'underwater scene', 'mountain peak', 'ocean wave'
        ]
        
        for phrase in compound_phrases:
            if all(word in query_lower for word in phrase.split()):
                phrases.insert(0, phrase)
        
        main_subjects = [
            'sunset', 'sunrise', 'ocean', 'sea', 'beach', 'mountain', 'forest',
            'city', 'street', 'building', 'waterfall', 'river', 'lake', 'desert',
            'garden', 'park', 'tree', 'flower', 'sky', 'cloud', 'wave', 'snow',
            'rain', 'storm', 'fire', 'water', 'light', 'night', 'day', 'road',
            'highway', 'bridge', 'tower', 'landscape', 'nature', 'wildlife',
            'bird', 'fish', 'animal', 'people', 'crowd', 'traffic', 'drone',
            'aerial', 'timelapse', 'underwater', 'volcano', 'aurora', 'rainbow',
            'canyon', 'valley', 'cliff', 'island', 'glacier'
        ]
        
        found_subjects = [subject for subject in main_subjects if subject in query_lower]
        phrases.extend(found_subjects[:4])
        
        action_words = ['crashing', 'flowing', 'moving', 'walking', 'running', 'flying',
                       'setting', 'rising', 'shining', 'glowing', 'falling', 'floating',
                       'swaying', 'blowing', 'burning', 'blooming', 'swimming', 'driving']
        for action in action_words:
            if action in query_lower:
                words = query_lower.split()
                if action in words:
                    idx = words.index(action)
                    if idx > 0:
                        phrases.append(f"{words[idx-1]} {action}")
                    if idx < len(words) - 1:
                        phrases.append(f"{action} {words[idx+1]}")
        
        seen = set()
        unique_phrases = []
        for phrase in phrases:
            if phrase not in seen and len(phrase.split()) >= 1:
                seen.add(phrase)
                unique_phrases.append(phrase)
        
        if not unique_phrases:
            words = [w for w in query_lower.split() if len(w) > 3]
            if len(words) >= 2:
                unique_phrases = [' '.join(words[:2]), ' '.join(words[-2:])]
            elif words:
                unique_phrases = words[:2]
        
        logger.info(f" Extracted key phrases: {unique_phrases[:5]}")
        return unique_phrases
    
    def _extract_primary_subject(self, query: str) -> Optional[str]:
        """
        Extract the single most important subject from the query.
        """
        query_lower = query.lower()
        
        priority_subjects = [
            'sunset', 'sunrise', 'waterfall', 'volcano', 'aurora', 'rainbow',
            'ocean', 'sea', 'beach', 'mountain', 'forest', 'desert', 'canyon',
            'valley', 'cliff', 'river', 'lake', 'island', 'glacier',
            'city', 'street', 'highway', 'bridge', 'building', 'skyline', 'downtown',
            'tree', 'flower', 'cloud', 'wave', 'snow', 'rain', 'storm', 'fire',
            'water', 'sky', 'sun', 'moon', 'star',
            'nature', 'landscape', 'wildlife', 'people', 'traffic', 'light'
        ]
        
        for subject in priority_subjects:
            if subject in query_lower:
                logger.info(f" Primary subject: '{subject}'")
                return subject
        
        words = [w for w in query_lower.split() if len(w) > 3]
        if words:
            logger.info(f" Primary subject (fallback): '{words[0]}'")
            return words[0]
        
        return None
    
    def _calculate_relevance_score(self, video: Dict, query: str) -> float:
        """
        Calculate relevance score for a video based on the search query.
        Higher score means better match to user intent.
        """
        score = 0.0
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Duration scoring (prefer 5-20s for most use cases)
        duration = video.get('duration', 0)
        if 5 <= duration <= 20:
            score += 3.0  # Ideal duration
        elif 3 <= duration <= 30:
            score += 2.0  # Good duration
        elif duration > 0:
            score += 1.0  # Any duration is better than none
        
        # Quality/Resolution scoring
        width = video.get('width', 0)
        height = video.get('height', 0)
        if width >= 1920 and height >= 1080:  # Full HD or better
            score += 3.0
        elif width >= 1280 and height >= 720:  # HD
            score += 2.0
        elif width >= 640 and height >= 480:  # SD
            score += 1.0
        
        # Quality tag scoring
        quality = video.get('quality', '').lower()
        if 'hd' in quality or 'high' in quality:
            score += 1.5
        
        # Video tags/description matching (if available)
        video_tags = video.get('tags', [])
        if video_tags:
            matching_tags = sum(1 for tag in video_tags if any(word in tag.lower() for word in query_words))
            score += matching_tags * 0.5
        
        # File size (prefer reasonably sized files for better loading)
        file_size = video.get('size', 0)
        if 1_000_000 < file_size < 50_000_000:  # 1MB - 50MB is good range
            score += 0.5
        
        return score
    
    def _extract_video_info(self, video: Dict, min_duration: int) -> Optional[Dict]:
        """
        Extract relevant information from a Pexels video object.
        """
        try:
            duration = video.get("duration", 0)
            if duration < min_duration:
                return None
                
            video_files = video.get("video_files", [])
            if not video_files:
                return None
                
            fast_link = get_fast_video_link(video_files)
            if not fast_link:
                return None
            
            selected_file = next((f for f in video_files if f.get('link') == fast_link), video_files[0])
            
            image_url = video.get("image")  # Pexels provides thumbnail in 'image' field
            if not image_url:
                video_pictures = video.get("video_pictures", [])
                if video_pictures:
                    image_url = video_pictures[0].get("picture")
            
            return {
                "id": video.get("id"),
                "url": fast_link,
                "image": image_url,  # Thumbnail URL
                "sd_video_link": fast_link,  # SD quality link for fast loading
                "width": selected_file.get("width", 1280),
                "height": selected_file.get("height", 720),
                "duration": duration,
                "file_type": selected_file.get("file_type", "video/mp4"),
                "quality": selected_file.get("quality", "sd"),
                "size": selected_file.get("file_size", 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting video info: {e}")
            return None
    
    def download_video(self, video_info: Dict, filename: str = None) -> Optional[str]:
        try:
            if not filename:
                timestamp = int(time.time())
                filename = f"pexels_video_{timestamp}_{video_info['id']}.mp4"
            elif not filename.endswith('.mp4'):
                filename += '.mp4'
                
            output_path = os.path.join("assets/videos", filename)
            
            logger.info(f" Downloading video: {filename}")
            
            response = requests.get(video_info["url"], stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = os.path.getsize(output_path)
            if file_size < 1000:
                os.remove(output_path)
                logger.error("Downloaded file too small, likely corrupt")
                return None
                
            logger.info(f" Downloaded: {filename} ({file_size / (1024*1024):.1f} MB)")
            return output_path
            
        except Exception as e:
            logger.error(f" Failed to download video: {e}")
            return None
    
    def download_multiple_videos(self, video_list: List[Dict], base_filename: str = "pexels_video") -> List[str]:
        downloaded_paths = []
        
        for i, video_info in enumerate(video_list):
            filename = f"{base_filename}_{i}.mp4"
            path = self.download_video(video_info, filename)
            if path:
                downloaded_paths.append(path)
                
        logger.info(f" Downloaded {len(downloaded_paths)}/{len(video_list)} videos")
        return downloaded_paths
    
    def generate_video_compilation(self, prompt: str, duration: int = 10, num_clips: int = 3) -> Optional[str]:
        try:
            logger.info(f" Generating video compilation for: '{prompt}'")
            
            search_query, params = process_prompt_for_pexels(prompt)
            logger.info(f" Processed prompt to: '{search_query}' with params {params}")
            
            videos = self.search_videos(prompt, num_clips * 2, min_duration=2)
            if not videos:
                logger.warning("No suitable videos found for compilation")
                return None
            
            selected_videos = videos[:num_clips]
            downloaded_paths = self.download_multiple_videos(selected_videos, f"compilation_{int(time.time())}")
            
            if not downloaded_paths:
                logger.warning("No videos were successfully downloaded")
                return None
            
            return self._create_compilation(downloaded_paths, duration)
            
        except Exception as e:
            logger.error(f" Failed to generate video compilation: {e}")
            return None
    
    def _create_compilation(self, video_paths: List[str], target_duration: int) -> Optional[str]:
        try:
            from moviepy import VideoFileClip, concatenate_videoclips
            
            clips = []
            clip_duration = target_duration / len(video_paths)
            
            for path in video_paths:
                try:
                    clip = VideoFileClip(path)
                    
                    if clip.duration > clip_duration:
                        clip = clip.subclipped(0, clip_duration)
                    
                    clip = clip.resized(height=1080)
                    
                    clips.append(clip)
                    
                except Exception as e:
                    logger.warning(f"Failed to process clip {path}: {e}")
                    continue
            
            if not clips:
                logger.error("No clips could be processed")
                return None
            
            final_clip = concatenate_videoclips(clips, method="compose")
            
            output_filename = f"pexels_compilation_{int(time.time())}.mp4"
            output_path = os.path.join("assets/videos", output_filename)
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30
            )
            
            for clip in clips:
                clip.close()
            final_clip.close()
            
            logger.info(f" Generated compilation: {output_filename}")
            return output_path
            
        except ImportError:
            logger.error("MoviePy not available for video compilation")
            return None
        except Exception as e:
            logger.error(f" Failed to create compilation: {e}")
            return None
    
    def generate_slideshow_video(self, prompt: str, duration: int = 10) -> Optional[str]:
        try:
            images = self.search_images(prompt, count=5)
            if not images:
                logger.warning("No images found for slideshow")
                return None
            
            downloaded_images = self.download_images(images, f"slideshow_{int(time.time())}")
            if not downloaded_images:
                logger.warning("No images were downloaded")
                return None
            
            return self._create_slideshow(downloaded_images, duration)
            
        except Exception as e:
            logger.error(f" Failed to generate slideshow: {e}")
            return None
    
    def search_images(self, query: str, count: int = 5) -> List[Dict]:
        """
        Search for images on Pexels using optimized keyword extraction.
        Focuses on the most relevant keywords for accurate results.
        """
        if not self.api_key:
            return []
            
        try:
            # Extract clean, focused keywords if query is long
            if len(query.split()) > 8:
                optimized_query = extract_keywords_for_pexels(query, max_keywords=6)
                logger.info(f"🔍 Optimized query: '{query}' → '{optimized_query}'")
                query = optimized_query
            else:
                logger.info(f"🔍 Searching Pexels images for: '{query}'")
            
            url = f"{self.base_url}/v1/search"
            all_images = []
            seen_ids = set()
            
            # Strategy 1: Direct keyword search (most accurate)
            logger.info("  Strategy 1: Direct keyword search...")
            params = {
                "query": query,
                "per_page": min(count * 3, 80),
                "orientation": "landscape"
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                for photo in data.get("photos", []):
                    img_id = photo.get("id")
                    if img_id not in seen_ids:
                        seen_ids.add(img_id)
                        all_images.append({
                            "id": img_id,
                            "url": photo["src"]["large"],
                            "width": photo.get("width"),
                            "height": photo.get("height"),
                            "photographer": photo.get("photographer", "Unknown"),
                            "alt": photo.get("alt", ""),
                            "relevance_score": 3.0  # Highest priority
                        })
                logger.info(f"    Found {len(data.get('photos', []))} images with full prompt")
            except Exception as e:
                logger.warning(f"    Full prompt search failed: {e}")
            
            # Strategy 2: Individual keyword search for variety
            if len(all_images) < count * 1.5:
                logger.info("  Strategy 2: Individual keyword search...")
                keywords = query.split()[:4]  # Take top 4 keywords
                for keyword in keywords:
                    if len(keyword) < 3:
                        continue
                    try:
                        params['query'] = keyword
                        params['per_page'] = min(count, 30)
                        
                        response = requests.get(url, headers=self.headers, params=params, timeout=15)
                        response.raise_for_status()
                        data = response.json()
                        
                        for photo in data.get("photos", []):
                            img_id = photo.get("id")
                            if img_id not in seen_ids:
                                seen_ids.add(img_id)
                                all_images.append({
                                    "id": img_id,
                                    "url": photo["src"]["large"],
                                    "width": photo.get("width"),
                                    "height": photo.get("height"),
                                    "photographer": photo.get("photographer", "Unknown"),
                                    "alt": photo.get("alt", ""),
                                    "relevance_score": 2.0
                                })
                        logger.info(f"    Keyword '{keyword}': {len(data.get('photos', []))} images")
                        
                        if len(all_images) >= count * 2:
                            break
                    except Exception as e:
                        logger.warning(f"    Keyword search '{keyword}' failed: {e}")
            
            # Strategy 3: Broader search if still not enough results
            if len(all_images) < count:
                logger.info("  Strategy 3: Broader category search...")
                # Extract first significant word as fallback
                words = [w for w in query.split() if len(w) > 3]
                if words:
                    primary = words[0]
                    try:
                        params['query'] = primary
                        params['per_page'] = min(count * 2, 50)
                        
                        response = requests.get(url, headers=self.headers, params=params, timeout=15)
                        response.raise_for_status()
                        data = response.json()
                        
                        for photo in data.get("photos", []):
                            img_id = photo.get("id")
                            if img_id not in seen_ids:
                                seen_ids.add(img_id)
                                all_images.append({
                                    "id": img_id,
                                    "url": photo["src"]["large"],
                                    "width": photo.get("width"),
                                    "height": photo.get("height"),
                                    "photographer": photo.get("photographer", "Unknown"),
                                    "alt": photo.get("alt", ""),
                                    "relevance_score": 1.0
                                })
                        logger.info(f"    Category '{primary}': {len(data.get('photos', []))} images")
                    except Exception as e:
                        logger.warning(f"    Broader search failed: {e}")
            
            # Sort by relevance and quality
            all_images.sort(key=lambda x: (
                x.get('relevance_score', 0),
                x.get('width', 0) * x.get('height', 0)
            ), reverse=True)
            
            # Return best matches
            result_images = all_images[:count]
            logger.info(f"✅ Returning {len(result_images)} best matching images")
            
            return result_images
            
        except Exception as e:
            logger.error(f"❌ Failed to search images: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def download_images(self, image_list: List[Dict], base_filename: str) -> List[str]:
        downloaded_paths = []
        
        for i, image_info in enumerate(image_list):
            try:
                filename = f"{base_filename}_{i}.jpg"
                output_path = os.path.join("assets/images", filename)
                
                response = requests.get(image_info["url"], timeout=20)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_paths.append(output_path)
                
            except Exception as e:
                logger.warning(f"Failed to download image {i}: {e}")
                
        return downloaded_paths
    
    def _create_slideshow(self, image_paths: List[str], duration: int) -> Optional[str]:
        try:
            from moviepy import ImageClip, concatenate_videoclips
            
            clips = []
            clip_duration = duration / len(image_paths)
            
            for path in image_paths:
                try:
                    clip = ImageClip(path, duration=clip_duration)
                    clip = clip.resized(height=1080)
                    clips.append(clip)
                except Exception as e:
                    logger.warning(f"Failed to process image {path}: {e}")
            
            if not clips:
                return None
            
            final_clip = concatenate_videoclips(clips, method="compose")
            
            output_filename = f"pexels_slideshow_{int(time.time())}.mp4"
            output_path = os.path.join("assets/videos", output_filename)
            
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                fps=30
            )
            
            final_clip.close()
            for clip in clips:
                clip.close()
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to create slideshow: {e}")
            return None
    
    def get_video_info(self, video_id: int) -> Optional[Dict]:
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/videos/videos/{video_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return None
    
    def get_learning_insights(self) -> Optional[Dict]:
        """
        Get insights from the learning system.
        Returns statistics and patterns learned from user prompts.
        """
        if not self.learner:
            return None
        
        try:
            return self.learner.get_insights()
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            return None
    
    def get_prompt_analysis(self, prompt: str) -> Optional[Dict]:
        """
        Analyze a prompt and get recommendations.
        Useful for showing users what the AI understands about their prompt.
        """
        if not self.learner:
            return None
        
        try:
            return self.learner.analyze_prompt(prompt)
        except Exception as e:
            logger.error(f"Failed to analyze prompt: {e}")
            return None

def test_pexels_video_generator():
    generator = PexelsVideoGenerator()
    
    print(" Testing Pexels Video Generator...")
    
    videos = generator.search_videos("ocean waves", count=3)
    print(f"Found {len(videos)} videos")
    
    if videos:
        first_video = videos[0]
        path = generator.download_video(first_video, "test_ocean_video")
        if path:
            print(f" Downloaded test video: {path}")
        
        compilation_path = generator.generate_video_compilation("ocean waves", duration=15, num_clips=3)
        if compilation_path:
            print(f" Generated compilation: {compilation_path}")
    
    slideshow_path = generator.generate_slideshow_video("beautiful landscape", duration=10)
    if slideshow_path:
        print(f" Generated slideshow: {slideshow_path}")
    
    print(" Pexels Video Generator test complete!")

if __name__ == "__main__":
    test_pexels_video_generator()
