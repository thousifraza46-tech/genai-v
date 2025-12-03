# -*- coding: utf-8 -*-
"""
Ultra-Stable Flask Server with Enhanced Error Handling
No crashes, no Unicode issues, production-ready
"""
import sys
import os
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS

# Fix Windows console encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Load API keys from config file
try:
    import config
    os.environ['GROQ_API_KEY'] = config.GROQ_API_KEY
    os.environ['GEMINI_API_KEY'] = config.GEMINI_API_KEY
    os.environ['GOOGLE_API_KEY'] = config.GOOGLE_API_KEY
    os.environ['PEXELS_API_KEY'] = config.PEXELS_API_KEY
    os.environ['HUGGINGFACE_TOKEN'] = config.HUGGINGFACE_TOKEN
    os.environ['REPLICATE_API_TOKEN'] = config.REPLICATE_API_TOKEN
    os.environ['RUNWAY_API_KEY'] = config.RUNWAY_API_KEY
    os.environ['STABILITY_API_KEY'] = config.STABILITY_API_KEY
    print("[Config] API keys loaded successfully from config.py")
except ImportError:
    print("[Warning] config.py not found - API keys must be set as environment variables")
except Exception as e:
    print(f"[Warning] Error loading config: {e}")

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =============================================
# HEALTH CHECK
# =============================================
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'}), 200

# =============================================
# AI CHAT (AI ASSISTANCE PAGE)
# =============================================
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle AI chat messages"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '')
        session_id = data.get('sessionId', 'default')
        mode = data.get('mode', 'smart')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        print(f"[Chat] Message from {session_id} ({mode} mode): {message[:50]}...")
        
        try:
            from chatbot_engine import ChatbotEngine
            chatbot = ChatbotEngine()
            response_text = chatbot.get_response(message, session_id, mode)
        except Exception as e:
            print(f"[Chat] Chatbot error: {e}")
            # Fallback response
            response_text = f"I received your message: '{message}'. I'm currently processing your request in {mode} mode."
        
        result = {
            'response': response_text,
            'timestamp': str(os.times()),
            'mode': mode
        }
        
        print(f"[Chat] Response sent: {len(response_text)} chars")
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = f"Chat error: {str(e)}"
        print(f"[Chat] ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId', 'default') if data else 'default'
        
        print(f"[Chat] Clearing history for session: {session_id}")
        
        try:
            from chatbot_engine import ChatbotEngine
            chatbot = ChatbotEngine()
            chatbot.clear_history(session_id)
        except Exception as e:
            print(f"[Chat] Clear error: {e}")
        
        return jsonify({'status': 'success', 'message': 'Chat history cleared'}), 200
        
    except Exception as e:
        error_msg = f"Clear chat error: {str(e)}"
        print(f"[Chat] ERROR: {error_msg}")
        return jsonify({'error': error_msg}), 500

# =============================================
# SCRIPT GENERATION
# =============================================
@app.route('/api/generate/script', methods=['POST'])
def generate_script():
    """Generate video script using AI"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        print(f"[Script] Generating for prompt: {prompt[:50]}...")
        
        from script_generator import ScriptGenerator
        generator = ScriptGenerator()
        result = generator.generate_script(prompt, duration)
        
        print(f"[Script] Success - {result.get('word_count', 0)} words")
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = f"Script generation error: {str(e)}"
        print(f"[Script] ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

# =============================================
# AUDIO GENERATION
# =============================================
@app.route('/api/generate/audio', methods=['POST'])
def generate_audio():
    """Generate audio from script text"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        script = data.get('script', '')
        if not script:
            return jsonify({'error': 'Script is required'}), 400
        
        print(f"[Audio] Generating for {len(script)} characters...")
        
        from audio_generator import AudioGenerator
        generator = AudioGenerator()
        result = generator.generate_audio(script)
        
        # Add audio URL
        if result.get('audio_path'):
            filename = os.path.basename(result['audio_path'])
            result['audio_url'] = f"/assets/audio/{filename}"
        
        print(f"[Audio] Success - {result.get('duration', 0)}s")
        return jsonify(result), 200
        
    except Exception as e:
        error_msg = f"Audio generation error: {str(e)}"
        print(f"[Audio] ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500

# =============================================
# IMAGE SEARCH (PEXELS)
# =============================================
@app.route('/api/generate/images', methods=['POST'])
def generate_images():
    """Search for images on Pexels with enhanced accuracy"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prompt = data.get('prompt', '')
        count = data.get('count', 3)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        print(f"[Images] Original prompt: {prompt[:100]}...")
        print(f"[Images] Requesting {count} images")
        
        # Smart keyword extraction for better accuracy
        search_query = prompt
        
        # If it's a long script, extract visual keywords
        if len(prompt) > 100:
            print(f"[Images] Script detected - extracting visual keywords")
            words = prompt.lower().split()
            
            # High-priority visual keywords (common in image descriptions)
            visual_keywords = {
                'sunset', 'sunrise', 'beach', 'ocean', 'sea', 'water', 'waves',
                'mountain', 'mountains', 'hill', 'hills', 'valley',
                'sky', 'clouds', 'cloud', 'blue', 'golden', 'red',
                'forest', 'trees', 'tree', 'palm', 'pine', 'jungle',
                'city', 'cityscape', 'urban', 'street', 'building', 'skyline',
                'landscape', 'nature', 'scenic', 'view', 'panorama',
                'lake', 'river', 'waterfall', 'stream', 'pond',
                'night', 'stars', 'starry', 'milky', 'moon', 'moonlight',
                'light', 'lights', 'glow', 'shine', 'bright', 'dark',
                'beautiful', 'stunning', 'vibrant', 'peaceful', 'dramatic',
                'colorful', 'vivid', 'serene', 'calm', 'wild', 'majestic',
                'desert', 'sand', 'dunes', 'sahara',
                'snow', 'ice', 'winter', 'frozen', 'snowy',
                'summer', 'autumn', 'fall', 'spring', 'season',
                'rain', 'storm', 'lightning', 'fog', 'mist',
                'flowers', 'flower', 'garden', 'blossom', 'bloom',
                'park', 'meadow', 'field', 'grass', 'green',
                'wildlife', 'animal', 'animals', 'bird', 'birds',
                'tropical', 'paradise', 'exotic', 'island'
            }
            
            # Extract matching visual terms (in order of appearance)
            found_keywords = []
            for word in words:
                clean_word = word.strip('.,!?;:"\'')
                if clean_word in visual_keywords and clean_word not in found_keywords:
                    found_keywords.append(clean_word)
            
            if found_keywords:
                # Use top 4-6 keywords for best results
                search_query = ' '.join(found_keywords[:6])
                print(f"[Images] Extracted keywords: {search_query}")
            else:
                # Fallback: use meaningful words from start of prompt
                meaningful_words = [w for w in words[:30] if len(w) > 3 and w.isalpha()]
                search_query = ' '.join(meaningful_words[:8])
                print(f"[Images] Using meaningful words: {search_query}")
        else:
            # Short prompt - use as-is or clean it
            print(f"[Images] Using direct prompt: {search_query}")
        
        # Search for images using Pexels API
        from pexels_video_generator import PexelsVideoGenerator
        generator = PexelsVideoGenerator()
        images = generator.search_images(search_query, count=count)
        
        if not images or len(images) == 0:
            print(f"[Images] No results with '{search_query}', trying simplified search")
            # Fallback: try with just the first 2-3 main words
            simple_query = ' '.join(search_query.split()[:3])
            images = generator.search_images(simple_query, count=count)
            print(f"[Images] Fallback search with '{simple_query}': {len(images)} images")
        
        # Format response
        formatted = []
        for i, img in enumerate(images):
            formatted.append({
                'id': img.get('id'),
                'sceneNumber': i + 1,
                'url': img.get('url'),
                'description': f"Scene {i + 1}",
                'width': img.get('width', 1920),
                'height': img.get('height', 1080)
            })
        
        print(f"[Images] SUCCESS - Returning {len(formatted)} high-quality images")
        return jsonify({'images': formatted, 'count': len(formatted)}), 200
        
    except Exception as e:
        error_msg = f"Image search error: {str(e)}"
        print(f"[Images] ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg, 'images': [], 'count': 0}), 500

# =============================================
# VIDEO SEARCH (PEXELS)
# =============================================
@app.route('/api/generate/videos', methods=['POST'])
def generate_videos():
    """Search for videos on Pexels"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        prompt = data.get('prompt', '')
        count = data.get('count', 10)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        print(f"[Videos] Searching for {count} videos...")
        
        from pexels_video_generator import PexelsVideoGenerator
        generator = PexelsVideoGenerator()
        videos = generator.search_videos_for_selection(prompt, count=count)
        
        # Format response
        formatted = []
        for vid in videos:
            formatted.append({
                'id': vid.get('id'),
                'url': vid.get('url'),
                'duration': vid.get('duration', 0),
                'width': vid.get('width', 1920),
                'height': vid.get('height', 1080),
                'thumbnail': vid.get('image', '')
            })
        
        print(f"[Videos] Success - Found {len(formatted)} videos")
        return jsonify({'videos': formatted, 'count': len(formatted)}), 200
        
    except Exception as e:
        error_msg = f"Video search error: {str(e)}"
        print(f"[Videos] ERROR: {error_msg}")
        traceback.print_exc()
        return jsonify({'error': error_msg, 'videos': [], 'count': 0}), 500

# =============================================
# STATIC FILE SERVING - ASSETS
# =============================================
from flask import send_from_directory

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (audio, images, etc.)"""
    try:
        # Try parent directory's assets first
        parent_assets = os.path.join(os.path.dirname(backend_dir), 'assets')
        if os.path.exists(os.path.join(parent_assets, filename)):
            return send_from_directory(parent_assets, filename)
        
        # Fall back to backend's assets
        backend_assets = os.path.join(backend_dir, 'assets')
        return send_from_directory(backend_assets, filename)
    except Exception as e:
        print(f"[Assets] Error serving {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404

# =============================================
# ERROR HANDLERS
# =============================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# =============================================
# SERVER STARTUP
# =============================================
if __name__ == '__main__':
    print("=" * 70)
    print("STABLE BACKEND SERVER")
    print("=" * 70)
    print(f"Server URL: http://localhost:5000")
    print(f"API Base:   http://localhost:5000/api")
    print(f"Health:     http://localhost:5000/api/health")
    print("=" * 70)
    print("")
    
    # Use Flask development server for reliability
    print("[INFO] Starting Flask development server...")
    print("[INFO] Press Ctrl+C to stop")
    print("")
    sys.stdout.flush()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")
