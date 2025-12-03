"""
Intelligent Video Generation Trainer
Learns from user feedback to continuously improve accuracy
Uses reinforcement learning principles to optimize video generation
"""

import json
import os
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentTrainer:
    """
    Self-learning system that improves video generation accuracy through user feedback
    """
    
    def __init__(self, data_dir: str = "ai_training_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.feedback_file = self.data_dir / "user_feedback.json"
        self.prompt_patterns_file = self.data_dir / "successful_patterns.json"
        self.query_optimization_file = self.data_dir / "query_optimizations.json"
        self.video_preferences_file = self.data_dir / "video_preferences.json"
        
        self.feedback_history = self._load_json(self.feedback_file, [])
        self.successful_patterns = self._load_json(self.prompt_patterns_file, {})
        self.query_optimizations = self._load_json(self.query_optimization_file, {})
        self.video_preferences = self._load_json(self.video_preferences_file, {})
        
        logger.info(f" Intelligent Trainer initialized with {len(self.feedback_history)} training examples")
    
    def _load_json(self, filepath: Path, default):
        """Load JSON data with fallback to default"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return default
        return default
    
    def _save_json(self, filepath: Path, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save {filepath}: {e}")
    
    def record_user_feedback(self, prompt: str, generated_content: Dict, 
                            user_rating: int, user_comments: str = "") -> None:
        """
        Record user feedback for continuous learning
        
        Args:
            prompt: User's original prompt
            generated_content: What was generated (videos, script, etc.)
            user_rating: 1-5 stars rating
            user_comments: Optional user comments
        """
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "generated_content": generated_content,
            "rating": user_rating,
            "comments": user_comments,
            "learned": False
        }
        
        self.feedback_history.append(feedback_entry)
        self._save_json(self.feedback_file, self.feedback_history)
        
        if user_rating >= 4:
            self._learn_from_success(prompt, generated_content)
            logger.info(f" Learned from successful generation (rating: {user_rating}/5)")
        elif user_rating <= 2:
            self._learn_from_failure(prompt, generated_content, user_comments)
            logger.info(f" Learned from unsuccessful generation (rating: {user_rating}/5)")
    
    def _learn_from_success(self, prompt: str, generated_content: Dict):
        """Learn patterns from successful generations"""
        
        key_elements = self._extract_key_elements(prompt)
        
        pattern_key = self._get_pattern_key(prompt)
        
        if pattern_key not in self.successful_patterns:
            self.successful_patterns[pattern_key] = {
                "count": 0,
                "examples": [],
                "key_elements": key_elements,
                "search_queries": [],
                "video_characteristics": []
            }
        
        self.successful_patterns[pattern_key]["count"] += 1
        self.successful_patterns[pattern_key]["examples"].append(prompt)
        
        if "search_query" in generated_content:
            query = generated_content["search_query"]
            if query not in self.successful_patterns[pattern_key]["search_queries"]:
                self.successful_patterns[pattern_key]["search_queries"].append(query)
        
        if "videos" in generated_content:
            for video in generated_content["videos"]:
                self.successful_patterns[pattern_key]["video_characteristics"].append({
                    "resolution": f"{video.get('width', 0)}x{video.get('height', 0)}",
                    "duration": video.get("duration", 0),
                    "quality": video.get("quality", "unknown")
                })
        
        self._save_json(self.prompt_patterns_file, self.successful_patterns)
    
    def _learn_from_failure(self, prompt: str, generated_content: Dict, comments: str):
        """Learn what NOT to do from failed generations"""
        
        pattern_key = self._get_pattern_key(prompt)
        
        if "search_query" in generated_content:
            query = generated_content["search_query"]
            
            if pattern_key not in self.query_optimizations:
                self.query_optimizations[pattern_key] = {
                    "failed_queries": [],
                    "suggestions": []
                }
            
            self.query_optimizations[pattern_key]["failed_queries"].append({
                "query": query,
                "reason": comments,
                "timestamp": datetime.now().isoformat()
            })
            
            suggestions = self._generate_improvement_suggestions(prompt, comments)
            self.query_optimizations[pattern_key]["suggestions"].extend(suggestions)
        
        self._save_json(self.query_optimization_file, self.query_optimizations)
    
    def _extract_key_elements(self, prompt: str) -> Dict:
        """Extract key visual elements from prompt"""
        import re
        
        prompt_lower = prompt.lower()
        
        elements = {
            "subjects": [],
            "settings": [],
            "time_of_day": [],
            "mood": [],
            "colors": [],
            "actions": []
        }
        
        subjects = [
            'ocean', 'sea', 'beach', 'mountain', 'forest', 'city', 'street',
            'waterfall', 'sunset', 'sunrise', 'sky', 'cloud', 'tree', 'flower',
            'building', 'road', 'bridge', 'lake', 'river', 'desert', 'snow',
            'rain', 'storm', 'fire', 'water', 'wave', 'bird', 'animal'
        ]
        
        times = ['morning', 'afternoon', 'evening', 'night', 'dawn', 'dusk', 
                'sunset', 'sunrise', 'golden hour', 'blue hour']
        
        moods = ['peaceful', 'calm', 'serene', 'dramatic', 'energetic', 'vibrant',
                'tranquil', 'majestic', 'beautiful', 'stunning', 'breathtaking']
        
        colors = ['blue', 'turquoise', 'golden', 'red', 'green', 'crystal clear',
                 'bright', 'dark', 'colorful', 'white', 'black']
        
        actions = ['crashing', 'flowing', 'moving', 'walking', 'running', 'flying',
                  'cascading', 'swaying', 'dancing', 'shining', 'glowing']
        
        for subject in subjects:
            if subject in prompt_lower:
                elements["subjects"].append(subject)
        
        for time_word in times:
            if time_word in prompt_lower:
                elements["time_of_day"].append(time_word)
        
        for mood in moods:
            if mood in prompt_lower:
                elements["mood"].append(mood)
        
        for color in colors:
            if color in prompt_lower:
                elements["colors"].append(color)
        
        for action in actions:
            if action in prompt_lower:
                elements["actions"].append(action)
        
        return elements
    
    def _get_pattern_key(self, prompt: str) -> str:
        """Generate a pattern key for categorizing similar prompts"""
        elements = self._extract_key_elements(prompt)
        
        key_parts = []
        
        if elements["subjects"]:
            key_parts.append(elements["subjects"][0])
        
        if elements["time_of_day"]:
            key_parts.append(elements["time_of_day"][0])
        
        if elements["mood"]:
            key_parts.append(elements["mood"][0])
        
        return "_".join(key_parts) if key_parts else "general"
    
    def optimize_prompt(self, prompt: str) -> str:
        """
        Optimize user's prompt based on learned patterns
        
        Returns enhanced prompt that will generate better results
        """
        pattern_key = self._get_pattern_key(prompt)
        
        if pattern_key in self.successful_patterns:
            pattern = self.successful_patterns[pattern_key]
            
            if pattern["search_queries"] and pattern["count"] >= 3:
                logger.info(f" Found {pattern['count']} successful examples for this pattern")
                
                successful_query = pattern["search_queries"][0]
                
                return self._apply_successful_structure(prompt, successful_query)
        
        return prompt
    
    def _apply_successful_structure(self, new_prompt: str, successful_query: str) -> str:
        """Apply successful query structure to new prompt"""
        return new_prompt
    
    def get_optimal_search_strategy(self, prompt: str) -> Dict:
        """
        Get optimal search strategy based on learned patterns
        
        Returns recommended settings for video search
        """
        pattern_key = self._get_pattern_key(prompt)
        
        strategy = {
            "use_exact_query": True,
            "min_duration": 3,
            "preferred_resolution": "UHD",
            "max_results": 6,
            "confidence": 0.5
        }
        
        if pattern_key in self.successful_patterns:
            pattern = self.successful_patterns[pattern_key]
            
            if pattern["count"] >= 5:
                strategy["confidence"] = 0.9
                
                if pattern["video_characteristics"]:
                    durations = [v.get("duration", 10) for v in pattern["video_characteristics"]]
                    avg_duration = sum(durations) / len(durations)
                    strategy["min_duration"] = max(3, int(avg_duration * 0.5))
                
                logger.info(f" High confidence strategy ({pattern['count']} examples)")
        
        return strategy
    
    def _generate_improvement_suggestions(self, prompt: str, feedback: str) -> List[str]:
        """Generate suggestions for improving failed prompts"""
        suggestions = []
        
        feedback_lower = feedback.lower() if feedback else ""
        
        if "not matching" in feedback_lower or "wrong" in feedback_lower:
            suggestions.append("Try adding more specific descriptive words")
            suggestions.append("Include time of day (morning, sunset, night)")
            suggestions.append("Add mood words (peaceful, dramatic, energetic)")
        
        if "quality" in feedback_lower or "low quality" in feedback_lower:
            suggestions.append("Specify '4K' or 'cinematic' in prompt")
            suggestions.append("Add 'high quality' or 'professional'")
        
        if "short" in feedback_lower or "duration" in feedback_lower:
            suggestions.append("Specify desired duration in prompt")
            suggestions.append("Request 'slow motion' or 'time-lapse' if appropriate")
        
        return suggestions
    
    def get_training_stats(self) -> Dict:
        """Get statistics about the training data"""
        total_feedback = len(self.feedback_history)
        
        if total_feedback == 0:
            return {
                "total_examples": 0,
                "average_rating": 0,
                "learned_patterns": 0,
                "confidence": 0
            }
        
        ratings = [f["rating"] for f in self.feedback_history if "rating" in f]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        successful = len([f for f in self.feedback_history if f.get("rating", 0) >= 4])
        
        return {
            "total_examples": total_feedback,
            "successful_examples": successful,
            "average_rating": round(avg_rating, 2),
            "learned_patterns": len(self.successful_patterns),
            "confidence": min(1.0, successful / 20),  # Confidence increases with successful examples
            "success_rate": round((successful / total_feedback * 100), 1) if total_feedback > 0 else 0
        }
    
    def suggest_prompt_improvements(self, prompt: str) -> List[str]:
        """Suggest improvements to user's prompt before generation"""
        suggestions = []
        elements = self._extract_key_elements(prompt)
        
        if not elements["time_of_day"]:
            suggestions.append(" Add time of day (e.g., 'at sunset', 'at night', 'during golden hour')")
        
        if not elements["mood"]:
            suggestions.append(" Add mood words (e.g., 'peaceful', 'dramatic', 'energetic')")
        
        if not elements["colors"]:
            suggestions.append(" Specify colors (e.g., 'turquoise water', 'golden light', 'vibrant colors')")
        
        if len(elements["subjects"]) == 0:
            suggestions.append(" Add specific subjects (e.g., 'ocean', 'mountain', 'city')")
        
        if len(prompt.split()) < 5:
            suggestions.append(" Add more details - longer prompts get better results")
        
        pattern_key = self._get_pattern_key(prompt)
        if pattern_key in self.successful_patterns:
            pattern = self.successful_patterns[pattern_key]
            if pattern["count"] >= 3:
                suggestions.insert(0, f" Similar prompts have {pattern['count']} successful examples")
        
        return suggestions

_trainer_instance = None

def get_trainer() -> IntelligentTrainer:
    """Get or create the global trainer instance"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = IntelligentTrainer()
    return _trainer_instance
