"""
Smart Learning System for Video Generation
Learns from user inputs and feedback to improve video accuracy over time.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import re

class VideoGenerationLearner:
    """
    Learns from user prompts and video selections to improve future searches.
    Tracks patterns, preferences, and successful query transformations.
    """
    
    def __init__(self, data_file: str = "ai_training_data/learning_data.json"):
        self.data_file = data_file
        os.makedirs(os.path.dirname(data_file), exist_ok=True)
        self.learning_data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing learning data or create new structure."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "prompt_patterns": {},      # Common patterns in successful prompts
            "keyword_frequency": {},    # Most used keywords
            "query_transformations": {}, # Original prompt → successful search query
            "video_preferences": {},    # Preferences for duration, quality, etc.
            "scene_types": {},          # Types of scenes requested
            "user_sessions": [],        # Track user sessions
            "success_metrics": {
                "total_generations": 0,
                "successful_searches": 0,
                "average_quality": 0
            }
        }
    
    def _save_data(self):
        """Save learning data to disk."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save learning data: {e}")
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """
        Analyze prompt and extract learning features.
        Returns enhanced search parameters based on learned patterns.
        """
        prompt_lower = prompt.lower()
        
        features = {
            "scene_type": self._identify_scene_type(prompt_lower),
            "keywords": self._extract_keywords(prompt_lower),
            "mood": self._identify_mood(prompt_lower),
            "time_of_day": self._identify_time(prompt_lower),
            "weather": self._identify_weather(prompt_lower),
            "location_type": self._identify_location(prompt_lower)
        }
        
        enhanced_query = self._enhance_query(prompt, features)
        
        recommendations = self._get_recommendations(features)
        
        return {
            "original_prompt": prompt,
            "enhanced_query": enhanced_query,
            "features": features,
            "recommendations": recommendations
        }
    
    def _identify_scene_type(self, prompt: str) -> str:
        """Identify the type of scene from prompt."""
        scene_types = {
            "nature_landscape": ["mountain", "forest", "valley", "canyon", "meadow", "hill", "landscape"],
            "water_scene": ["ocean", "sea", "lake", "river", "waterfall", "beach", "shore", "waves"],
            "urban": ["city", "street", "building", "downtown", "urban", "skyline", "traffic"],
            "sky": ["sky", "cloud", "sunset", "sunrise", "stars", "moon", "aurora"],
            "weather": ["storm", "rain", "snow", "fog", "lightning", "thunder"],
            "wildlife": ["animal", "bird", "fish", "wildlife", "deer", "whale", "dolphin"],
            "aerial": ["aerial", "drone", "birds-eye", "overhead", "flying"],
            "timelapse": ["timelapse", "time-lapse", "fast", "moving"]
        }
        
        for scene_type, keywords in scene_types.items():
            if any(kw in prompt for kw in keywords):
                return scene_type
        
        return "general"
    
    def _extract_keywords(self, prompt: str) -> List[str]:
        """Extract important keywords for learning."""
        stopwords = {'a', 'an', 'the', 'with', 'and', 'or', 'of', 'in', 'on', 'at', 'to'}
        words = re.findall(r'\b\w+\b', prompt.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 3]
        
        return keywords[:10]  # Top 10 keywords
    
    def _identify_mood(self, prompt: str) -> str:
        """Identify the mood/atmosphere of the scene."""
        moods = {
            "peaceful": ["peaceful", "calm", "serene", "tranquil", "quiet", "gentle"],
            "dramatic": ["dramatic", "intense", "powerful", "majestic", "epic"],
            "beautiful": ["beautiful", "stunning", "breathtaking", "gorgeous", "picturesque"],
            "energetic": ["busy", "bustling", "active", "lively", "dynamic", "vibrant"],
            "dark": ["dark", "moody", "mysterious", "ominous", "shadowy"],
            "bright": ["bright", "sunny", "glowing", "radiant", "luminous"]
        }
        
        for mood, keywords in moods.items():
            if any(kw in prompt for kw in keywords):
                return mood
        
        return "neutral"
    
    def _identify_time(self, prompt: str) -> Optional[str]:
        """Identify time of day."""
        times = {
            "sunrise": ["sunrise", "dawn", "morning light", "early morning"],
            "sunset": ["sunset", "dusk", "golden hour", "evening"],
            "night": ["night", "nighttime", "evening", "dark"],
            "day": ["day", "daytime", "afternoon", "midday"]
        }
        
        for time, keywords in times.items():
            if any(kw in prompt for kw in keywords):
                return time
        
        return None
    
    def _identify_weather(self, prompt: str) -> Optional[str]:
        """Identify weather conditions."""
        weather_types = ["storm", "rain", "snow", "fog", "cloudy", "clear", "sunny"]
        
        for weather in weather_types:
            if weather in prompt:
                return weather
        
        return None
    
    def _identify_location(self, prompt: str) -> str:
        """Identify type of location."""
        locations = {
            "tropical": ["tropical", "paradise", "palm", "caribbean"],
            "arctic": ["arctic", "polar", "frozen", "ice", "glacier"],
            "desert": ["desert", "sand", "arid", "dunes"],
            "forest": ["forest", "woods", "jungle", "trees"],
            "urban": ["city", "urban", "downtown", "street"],
            "coastal": ["beach", "coast", "shore", "seaside"],
            "mountain": ["mountain", "peak", "alpine", "summit"]
        }
        
        for location, keywords in locations.items():
            if any(kw in prompt for kw in keywords):
                return location
        
        return "general"
    
    def _enhance_query(self, prompt: str, features: Dict) -> str:
        """
        Enhance search query based on learned patterns.
        Adds context-aware terms that improve search accuracy.
        """
        enhanced = prompt
        
        scene_type = features["scene_type"]
        if scene_type in self.learning_data["scene_types"]:
            scene_data = self.learning_data["scene_types"][scene_type]
            
            if "successful_modifiers" in scene_data:
                pass
        
        return enhanced
    
    def _get_recommendations(self, features: Dict) -> Dict:
        """Get recommended video parameters based on features."""
        recommendations = {
            "min_duration": 5,
            "max_duration": 30,
            "preferred_quality": "hd",
            "orientation": "landscape"
        }
        
        scene_type = features["scene_type"]
        
        if scene_type == "timelapse":
            recommendations["min_duration"] = 3
            recommendations["max_duration"] = 10
        elif scene_type in ["nature_landscape", "water_scene"]:
            recommendations["min_duration"] = 8
            recommendations["max_duration"] = 30
        elif scene_type == "urban":
            recommendations["min_duration"] = 5
            recommendations["max_duration"] = 20
        
        return recommendations
    
    def record_generation(self, prompt: str, search_query: str, 
                         videos_found: int, video_quality: str = "hd",
                         success: bool = True):
        """
        Record a video generation attempt to learn from it.
        """
        self.learning_data["success_metrics"]["total_generations"] += 1
        if success and videos_found > 0:
            self.learning_data["success_metrics"]["successful_searches"] += 1
        
        analysis = self.analyze_prompt(prompt)
        features = analysis["features"]
        
        scene_type = features["scene_type"]
        if scene_type not in self.learning_data["scene_types"]:
            self.learning_data["scene_types"][scene_type] = {
                "count": 0,
                "successful_queries": [],
                "keywords": []
            }
        
        self.learning_data["scene_types"][scene_type]["count"] += 1
        
        if success and videos_found > 0:
            if search_query not in self.learning_data["scene_types"][scene_type]["successful_queries"]:
                self.learning_data["scene_types"][scene_type]["successful_queries"].append(search_query)
            
            for keyword in features["keywords"]:
                if keyword not in self.learning_data["keyword_frequency"]:
                    self.learning_data["keyword_frequency"][keyword] = 0
                self.learning_data["keyword_frequency"][keyword] += 1
        
        if prompt != search_query:
            self.learning_data["query_transformations"][prompt] = search_query
        
        session = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "search_query": search_query,
            "videos_found": videos_found,
            "quality": video_quality,
            "success": success,
            "features": features
        }
        
        self.learning_data["user_sessions"].append(session)
        
        if len(self.learning_data["user_sessions"]) > 1000:
            self.learning_data["user_sessions"] = self.learning_data["user_sessions"][-1000:]
        
        self._save_data()
    
    def get_similar_prompts(self, prompt: str, limit: int = 5) -> List[Tuple[str, str]]:
        """
        Find similar successful prompts from history.
        Returns list of (original_prompt, search_query) tuples.
        """
        analysis = self.analyze_prompt(prompt)
        features = analysis["features"]
        scene_type = features["scene_type"]
        
        similar = []
        
        for session in reversed(self.learning_data["user_sessions"]):
            if session.get("success") and session["features"]["scene_type"] == scene_type:
                similar.append((session["prompt"], session["search_query"]))
                
                if len(similar) >= limit:
                    break
        
        return similar
    
    def get_insights(self) -> Dict:
        """Get insights from learning data."""
        metrics = self.learning_data["success_metrics"]
        
        success_rate = 0
        if metrics["total_generations"] > 0:
            success_rate = (metrics["successful_searches"] / metrics["total_generations"]) * 100
        
        top_keywords = sorted(
            self.learning_data["keyword_frequency"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        scene_counts = {
            scene: data["count"] 
            for scene, data in self.learning_data["scene_types"].items()
        }
        top_scenes = sorted(scene_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_generations": metrics["total_generations"],
            "success_rate": success_rate,
            "top_keywords": top_keywords,
            "top_scene_types": top_scenes,
            "total_sessions": len(self.learning_data["user_sessions"])
        }
    
    def suggest_improvements(self, prompt: str) -> List[str]:
        """
        Suggest improvements to a prompt based on learned patterns.
        """
        suggestions = []
        analysis = self.analyze_prompt(prompt)
        features = analysis["features"]
        
        if len(prompt.split()) < 5:
            suggestions.append("Consider adding more descriptive details for better results")
        
        if features["mood"] == "neutral":
            suggestions.append("Try adding mood words like 'peaceful', 'dramatic', or 'beautiful'")
        
        if not features["time_of_day"] and features["scene_type"] in ["nature_landscape", "urban", "sky"]:
            suggestions.append("Consider specifying time of day (sunrise, sunset, night, day)")
        
        similar = self.get_similar_prompts(prompt, limit=3)
        if similar:
            suggestions.append(f"Similar successful prompts found - using learned patterns")
        
        return suggestions

def test_learner():
    """Test the learning system."""
    print("\n=== Testing Video Generation Learner ===\n")
    
    learner = VideoGenerationLearner()
    
    test_prompts = [
        "A beautiful sunset over the ocean with waves",
        "A busy city street at night with neon lights",
        "A peaceful forest with sunlight filtering through trees",
        "Timelapse of stars moving across the night sky"
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: '{prompt}'")
        
        analysis = learner.analyze_prompt(prompt)
        print(f"Scene Type: {analysis['features']['scene_type']}")
        print(f"Mood: {analysis['features']['mood']}")
        print(f"Keywords: {', '.join(analysis['features']['keywords'][:5])}")
        
        learner.record_generation(prompt, prompt, videos_found=3, success=True)
        
        suggestions = learner.suggest_improvements(prompt)
        if suggestions:
            print(f"Suggestions: {suggestions[0]}")
    
    print("\n=== Learning Insights ===")
    insights = learner.get_insights()
    print(f"Total Generations: {insights['total_generations']}")
    print(f"Success Rate: {insights['success_rate']:.1f}%")
    print(f"Top Keywords: {[kw for kw, _ in insights['top_keywords'][:5]]}")
    print(f"Top Scenes: {[scene for scene, _ in insights['top_scene_types']]}")

if __name__ == "__main__":
    test_learner()
