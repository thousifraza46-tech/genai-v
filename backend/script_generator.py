
import os
import json
import time
import random
from typing import Dict, Any, List, Optional

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print(" Google Generative AI not available for script generation")

class ScriptGenerator:
    
    def __init__(self):
        try:
            import config
            self.api_key = getattr(config, 'GEMINI_API_KEY', None)
        except ImportError:
            self.api_key = os.getenv('GOOGLE_API_KEY')
        
        self.ai_available = GENAI_AVAILABLE and self.api_key
        if self.ai_available:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print(" AI Script Generator initialized with Gemini")
            except Exception as e:
                print(f" Gemini initialization failed: {e}")
                self.ai_available = False
    
    def generate_script(self, video_prompt: str, duration: int = 30) -> Dict[str, Any]:
        print(f" Generating script for: '{video_prompt}'")
        
        if self.ai_available:
            return self._generate_with_ai(video_prompt, duration)
        else:
            return self._generate_fallback(video_prompt, duration)
    
    def _generate_with_ai(self, video_prompt: str, duration: int) -> Dict[str, Any]:
        try:
            target_words = int((duration / 60) * 150)
            
            system_prompt = f"""
You are a professional video script writer. Create a short, engaging narration script for a video with the following prompt:

VIDEO DESCRIPTION: {video_prompt}

Requirements:
- Create a professional, engaging narration script
- Target length: approximately {target_words} words (for a {duration}-second video)
- Use clear, concise language appropriate for a professional video
- Structure with introduction, main points, and conclusion
- Focus on visual elements that would appear in the video
- Use natural speech patterns and engaging tone

Return ONLY the script text without any notes, explanations, or formatting.
"""
            
            response = self.model.generate_content(system_prompt)
            script = response.text.strip()
            
            word_count = len(script.split())
            estimated_duration = int((word_count / 150) * 60)
            
            print(f" ✅ AI Script generated: {word_count} words, ~{estimated_duration}s")
            
            return {
                "script": script,
                "word_count": word_count,
                "estimated_duration": estimated_duration,
                "source": "gemini-ai"
            }
            
        except Exception as e:
            print(f" ⚠️ AI generation failed: {e}")
            return self._generate_fallback(video_prompt, duration)
    
    def _generate_fallback(self, video_prompt: str, duration: int) -> Dict[str, Any]:
        print(" Using fallback script generation")
        
        intros = [
            "Welcome to this fascinating look at {topic}.",
            "Today, we explore the incredible world of {topic}.",
            "Join us on an extraordinary journey through {topic}.",
            "In this video, we discover the amazing {topic}."
        ]
        
        middles = [
            "The {adjective} details reveal themselves as we look closer.",
            "What makes this truly {adjective} is how it {verb}.",
            "Experts consider this one of the most {adjective} examples in existence.",
            "As we can see, the {noun} demonstrates remarkable {quality}."
        ]
        
        conclusions = [
            "This concludes our exploration of {topic}.",
            "Thank you for joining us on this journey through {topic}.",
            "We hope you enjoyed this glimpse into the world of {topic}.",
            "Remember to appreciate the beauty of {topic} in your everyday life."
        ]
        
        keywords = [word for word in video_prompt.split() 
                   if len(word) > 3 and word.lower() not in ['with', 'this', 'that', 'from', 'there']]
        
        topic = ' '.join(keywords[:3]) if keywords else video_prompt
        noun = keywords[0] if keywords else "subject"
        adjective = random.choice(["fascinating", "remarkable", "stunning", "incredible"])
        verb = random.choice(["transforms", "evolves", "captivates", "inspires"])
        quality = random.choice(["complexity", "beauty", "elegance", "precision"])
        
        intro = random.choice(intros).format(topic=topic)
        middle_paragraphs = []
        
        num_paragraphs = max(1, min(5, duration // 10))
        
        for _ in range(num_paragraphs):
            paragraph = random.choice(middles).format(
                adjective=random.choice(["fascinating", "remarkable", "stunning", "incredible"]),
                verb=random.choice(["transforms", "evolves", "captivates", "inspires"]),
                noun=random.choice(keywords) if keywords else "subject",
                quality=random.choice(["complexity", "beauty", "elegance", "precision"])
            )
            middle_paragraphs.append(paragraph)
        
        conclusion = random.choice(conclusions).format(topic=topic)
        
        script = intro + " " + " ".join(middle_paragraphs) + " " + conclusion
        
        word_count = len(script.split())
        estimated_duration = int((word_count / 150) * 60)
        
        return {
            "script": script,
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "source": "fallback"
        }

if __name__ == "__main__":
    generator = ScriptGenerator()
    
    test_prompts = [
        "A robot dancing in a futuristic city",
        "Ocean waves crashing on a sunset beach",
        "A butterfly exploring a magical forest"
    ]
    
    for prompt in test_prompts:
        print("\n" + "=" * 50)
        print(f"Testing: {prompt}")
        script_data = generator.generate_script(prompt, duration=30)
        
        print(f"Source: {script_data['source']}")
        print(f"Word count: {script_data['word_count']}")
        print(f"Est. duration: {script_data['estimated_duration']}s")
        print("\nScript:")
        print("-" * 50)
        print(script_data['script'])
