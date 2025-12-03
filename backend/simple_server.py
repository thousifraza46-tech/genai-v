# -*- coding: utf-8 -*-
"""
Minimal Flask Server - Stable Version
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

@app.route('/api/generate/script', methods=['POST'])
def generate_script():
    try:
        from script_generator import ScriptGenerator
        data = request.get_json()
        prompt = data.get('prompt', '')
        duration = data.get('duration', 30)
        
        generator = ScriptGenerator()
        result = generator.generate_script(prompt, duration)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/audio', methods=['POST'])
def generate_audio():
    try:
        from audio_generator import AudioGenerator
        data = request.get_json()
        script = data.get('script', '')
        
        generator = AudioGenerator()
        result = generator.generate_audio(script)
        
        if result.get('audio_path'):
            filename = os.path.basename(result['audio_path'])
            result['audio_url'] = f"/assets/audio/{filename}"
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/images', methods=['POST'])
def generate_images():
    try:
        from pexels_video_generator import PexelsVideoGenerator
        data = request.get_json()
        prompt = data.get('prompt', '')
        count = data.get('count', 3)
        
        print(f"[Images API] Received prompt (length: {len(prompt)})")
        print(f"[Images API] Requesting {count} images")
        
        # If prompt is long (likely a script), extract key visual terms
        if len(prompt) > 100:
            print(f"[Images API] Long prompt detected, extracting key terms")
            # Extract keywords from script - focus on nouns, adjectives, visual descriptions
            words = prompt.lower().split()
            visual_keywords = []
            
            # Common visual terms and their priorities
            visual_terms = ['sunset', 'beach', 'ocean', 'mountain', 'sky', 'forest', 
                          'city', 'landscape', 'nature', 'water', 'light', 'night',
                          'beautiful', 'stunning', 'vibrant', 'peaceful', 'dramatic']
            
            # Extract visual terms from script
            for term in visual_terms:
                if term in words:
                    visual_keywords.append(term)
            
            # If we found visual keywords, use them
            if visual_keywords:
                search_query = ' '.join(visual_keywords[:4])
                print(f"[Images API] Using extracted terms: {search_query}")
            else:
                # Use first 50 words of script
                search_query = ' '.join(prompt.split()[:50])
        else:
            search_query = prompt
        
        generator = PexelsVideoGenerator()
        images = generator.search_images(search_query, count=count)
        
        print(f"[Images API] Found {len(images)} images")
        
        formatted = []
        for i, img in enumerate(images):
            formatted.append({
                'id': img['id'],
                'sceneNumber': i + 1,
                'url': img['url'],
                'description': f"Scene {i + 1}"
            })
        
        return jsonify({'images': formatted, 'count': len(formatted)})
    except Exception as e:
        print(f"[Images API] Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate/videos', methods=['POST'])
def generate_videos():
    try:
        from pexels_video_generator import PexelsVideoGenerator
        data = request.get_json()
        prompt = data.get('prompt', '')
        count = data.get('count', 10)
        
        generator = PexelsVideoGenerator()
        videos = generator.search_videos_for_selection(prompt, count=count)
        
        formatted = []
        for vid in videos:
            formatted.append({
                'id': vid['id'],
                'url': vid['url'],
                'duration': vid.get('duration', 0),
                'width': vid.get('width', 1920),
                'height': vid.get('height', 1080),
                'thumbnail': vid.get('image', '')
            })
        
        return jsonify({'videos': formatted, 'count': len(formatted)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Backend Server Starting...")
    print("Server: http://localhost:5000")
    print("API Base: http://localhost:5000/api")
    print("=" * 60)
    print("")
    
    try:
        from waitress import serve
        print("Using Waitress production server")
        serve(app, host='0.0.0.0', port=5000, threads=4)
    except ImportError:
        print("Using Flask development server")
        print("Install waitress for better performance: pip install waitress")
        print("")
        try:
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True, use_reloader=False)
        except Exception as e:
            print(f"ERROR starting server: {e}")
            import traceback
            traceback.print_exc()
            input("Press Enter to exit...")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
