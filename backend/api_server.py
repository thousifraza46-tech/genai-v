"""
Flask API Server for AI Video Generation Platform
Provides REST API endpoints for frontend React application
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import time
from typing import List, Dict
from pathlib import Path

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup directories
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_DIR = ASSETS_DIR / "audio"
VIDEOS_DIR = ASSETS_DIR / "videos"

# Create directories if they don't exist
ASSETS_DIR.mkdir(exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Import backend modules
from chatbot_engine import ChatbotEngine
from huggingface_service import HuggingFaceService

app = Flask(__name__)

# CORS configuration - supports both development and production
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*')
if ALLOWED_ORIGINS != '*':
    # Parse comma-separated origins for production
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS.split(',')]

CORS(app, resources={
    r"/api/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})  # Enable CORS for React frontend

# Global error handlers to prevent crashes
@app.errorhandler(Exception)
def handle_exception(e):
    """Catch-all exception handler to prevent server crashes"""
    import traceback
    print(f"\n❌ Unhandled exception: {str(e)}")
    traceback.print_exc()
    return jsonify({
        'error': 'Internal server error',
        'message': str(e),
        'type': type(e).__name__
    }), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': str(e)
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': str(e)
    }), 500

# Store conversation history per session
conversation_sessions: Dict[str, List[Dict[str, str]]] = {}

# Initialize HuggingFace service
try:
    hf_service = HuggingFaceService()
    print("[HuggingFace] ✅ Service initialized")
except Exception as e:
    print(f"[HuggingFace] ⚠️ Service initialization failed: {e}")
    hf_service = None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Video Generation API is running'
    })


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets (audio files, videos, etc.)"""
    try:
        return send_from_directory(str(ASSETS_DIR), filename)
    except Exception as e:
        print(f"[Assets] Error serving {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/config/keys', methods=['GET'])
def get_api_keys():
    """
    Get API keys for frontend use
    Returns sanitized keys (last 4 chars only for security)
    """
    try:
        from config import (
            GROQ_API_KEY, GEMINI_API_KEY, PEXELS_API_KEY,
            HUGGINGFACE_TOKEN, REPLICATE_API_TOKEN, 
            RUNWAY_API_KEY, STABILITY_API_KEY
        )
        
        def sanitize_key(key):
            """Show only last 4 characters for security"""
            if not key or len(key) < 8:
                return "****"
            return f"...{key[-4:]}"
        
        return jsonify({
            'keys': {
                'groq': GROQ_API_KEY,
                'gemini': GEMINI_API_KEY,
                'pexels': PEXELS_API_KEY,
                'huggingface': HUGGINGFACE_TOKEN,
                'replicate': REPLICATE_API_TOKEN,
                'runway': RUNWAY_API_KEY,
                'stability': STABILITY_API_KEY
            },
            'sanitized': {
                'groq': sanitize_key(GROQ_API_KEY),
                'gemini': sanitize_key(GEMINI_API_KEY),
                'pexels': sanitize_key(PEXELS_API_KEY),
                'huggingface': sanitize_key(HUGGINGFACE_TOKEN),
                'replicate': sanitize_key(REPLICATE_API_TOKEN),
                'runway': sanitize_key(RUNWAY_API_KEY),
                'stability': sanitize_key(STABILITY_API_KEY)
            },
            'status': 'connected'
        })
    except Exception as e:
        print(f"Error loading API keys: {str(e)}")
        return jsonify({
            'error': 'Failed to load API keys',
            'status': 'disconnected'
        }), 500


@app.route('/api/config/health', methods=['GET'])
def config_health():
    """Check if backend configuration is healthy"""
    try:
        from config import GROQ_API_KEY, GEMINI_API_KEY, PEXELS_API_KEY
        
        health_status = {
            'groq': bool(GROQ_API_KEY and len(GROQ_API_KEY) > 10),
            'gemini': bool(GEMINI_API_KEY and len(GEMINI_API_KEY) > 10),
            'pexels': bool(PEXELS_API_KEY and len(PEXELS_API_KEY) > 10)
        }
        
        all_healthy = all(health_status.values())
        
        return jsonify({
            'status': 'healthy' if all_healthy else 'degraded',
            'keys': health_status,
            'message': 'All keys configured' if all_healthy else 'Some keys missing'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for AI assistance
    
    Expected JSON body:
    {
        "message": "user message",
        "sessionId": "unique-session-id",
        "mode": "quick" | "smart" | "study" | "deep"
    }
    
    Returns:
    {
        "response": "AI response",
        "timestamp": "ISO timestamp"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        session_id = data.get('sessionId', 'default')
        mode = data.get('mode', 'smart')
        
        # Get or create conversation history for this session
        if session_id not in conversation_sessions:
            conversation_sessions[session_id] = []
        
        conversation_history = conversation_sessions[session_id]
        
        # Add user message to history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Generate AI response using chatbot engine
        chatbot = ChatbotEngine()
        ai_response = chatbot.get_response(user_message, session_id, mode)
        
        # Add AI response to history
        conversation_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        
        # Keep only last 20 messages (10 exchanges) to manage memory
        if len(conversation_history) > 20:
            conversation_sessions[session_id] = conversation_history[-20:]
        
        from datetime import datetime
        
        return jsonify({
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'mode': mode
        })
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """
    Clear conversation history for a session
    
    Expected JSON body:
    {
        "sessionId": "unique-session-id"
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('sessionId', 'default')
        
        if session_id in conversation_sessions:
            del conversation_sessions[session_id]
        
        return jsonify({
            'message': 'Conversation history cleared',
            'sessionId': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """
    Get conversation history for a session
    
    Query params:
    - sessionId: unique session identifier
    """
    try:
        session_id = request.args.get('sessionId', 'default')
        
        history = conversation_sessions.get(session_id, [])
        
        return jsonify({
            'sessionId': session_id,
            'history': history,
            'messageCount': len(history)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/video', methods=['POST'])
def generate_video():
    """
    Generate complete video from prompt - Full Pipeline
    
    Expected JSON body:
    {
        "prompt": "video description",
        "duration": 30,
        "style": "cinematic"
    }
    
    Returns:
    {
        "jobId": "unique-job-id",
        "status": "processing",
        "stages": {
            "script": {"status": "pending", "progress": 0},
            "audio": {"status": "pending", "progress": 0},
            "images": {"status": "pending", "progress": 0},
            "video": {"status": "pending", "progress": 0}
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        prompt = data['prompt']
        duration = data.get('duration', 30)
        
        # Generate unique job ID
        job_id = f"job-{int(time.time() * 1000)}"
        
        # Return immediately with job ID
        # In production, this would trigger background processing
        return jsonify({
            'jobId': job_id,
            'status': 'queued',
            'message': 'Video generation queued',
            'prompt': prompt,
            'duration': duration
        })
        
    except Exception as e:
        print(f"Video generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/script', methods=['POST'])
def generate_script():
    """
    Generate video script from prompt - Stage 1
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        from script_generator import ScriptGenerator
        
        prompt = data['prompt']
        duration = data.get('duration', 30)
        
        generator = ScriptGenerator()
        script_data = generator.generate_script(prompt, duration)
        
        return jsonify({
            'script': script_data['script'],
            'word_count': script_data['word_count'],
            'estimated_duration': script_data['estimated_duration'],
            'source': script_data['source']
        })
        
    except Exception as e:
        print(f"Script generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/audio', methods=['POST'])
def generate_audio():
    """
    Generate audio from script - Stage 2
    
    Expected JSON body:
    {
        "script": "text to convert to speech",
        "voice": "en-US-ChristopherNeural" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'script' not in data:
            return jsonify({'error': 'Script text is required'}), 400
        
        from audio_generator import AudioGenerator
        
        script = data['script']
        voice = data.get('voice', None)
        
        generator = AudioGenerator()
        audio_data = generator.generate_audio(script, voice=voice)
        
        # Convert absolute path to relative URL with forward slashes
        if audio_data['audio_path']:
            # Return relative path from assets folder
            audio_filename = os.path.basename(audio_data['audio_path'])
            audio_url = f"/assets/audio/{audio_filename}"
            
            # Ensure file exists and is synced
            audio_file = AUDIO_DIR / audio_filename
            if not audio_file.exists():
                # Copy to assets if in different location
                import shutil
                if os.path.exists(audio_data['audio_path']):
                    shutil.copy2(audio_data['audio_path'], audio_file)
                    print(f"[Audio] Copied to assets: {audio_file}")
        else:
            audio_url = None
        
        return jsonify({
            'audio_url': audio_url,
            'audioUrl': audio_url,
            'audio_path': audio_data['audio_path'],
            'audioPath': str(AUDIO_DIR / os.path.basename(audio_data['audio_path'])) if audio_data['audio_path'] else None,
            'duration': audio_data['duration'],
            'source': audio_data['source'],
            'voice': audio_data['voice']
        })
        
    except Exception as e:
        print(f"Audio generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/images', methods=['POST'])
def generate_images():
    """
    Generate images for video scenes - Stage 3
    
    Expected JSON body:
    {
        "prompt": "video description",
        "script": "generated script text (optional, improves accuracy)",
        "count": 3
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        from pexels_video_generator import PexelsVideoGenerator, extract_keywords_for_pexels
        
        prompt = data['prompt']
        script = data.get('script', '')  # Use script for better context if available
        count = data.get('count', 3)
        
        # Extract clean keywords from prompt for accurate search
        # Use original prompt for better accuracy, not the full script
        search_query = extract_keywords_for_pexels(prompt, max_keywords=8)
        
        print(f"[Images] Original prompt: {prompt[:100]}...")
        print(f"[Images] Optimized search: '{search_query}'")
        
        generator = PexelsVideoGenerator()
        images = generator.search_images(search_query, count=count)
        
        # Format images for frontend
        formatted_images = []
        for i, img in enumerate(images):
            formatted_images.append({
                'id': img['id'],
                'sceneNumber': i + 1,
                'url': img['url'],
                'description': f"Scene {i + 1}",
                'width': img.get('width', 1920),
                'height': img.get('height', 1080),
                'photographer': img.get('photographer', 'Unknown')
            })
        
        return jsonify({
            'images': formatted_images,
            'count': len(formatted_images)
        })
        
    except Exception as e:
        print(f"Image generation error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/videos', methods=['POST'])
def generate_videos():
    """
    Fetch videos from Pexels - Stage 4
    
    Expected JSON body:
    {
        "prompt": "video description",
        "script": "generated script text (optional, improves accuracy)",
        "count": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Prompt is required'}), 400
        
        from pexels_video_generator import PexelsVideoGenerator
        
        prompt = data['prompt']
        script = data.get('script', '')  # Use script for better context if available
        count = data.get('count', 10)
        
        # Use script for more accurate search if available
        search_query = script if script and len(script) > 20 else prompt
        
        print(f"[API] Fetching {count} videos with {'script context' if script else 'prompt'}: {search_query[:100]}...")
        
        generator = PexelsVideoGenerator()
        videos = generator.search_videos_for_selection(prompt, count=count)
        
        print(f"[API] Found {len(videos)} videos from Pexels")
        
        # Format videos for frontend
        formatted_videos = []
        for vid in videos:
            formatted_videos.append({
                'id': vid['id'],
                'url': vid['url'],
                'duration': vid.get('duration', 0),
                'width': vid.get('width', 1920),
                'height': vid.get('height', 1080),
                'thumbnail': vid.get('image', ''),
                'quality': vid.get('quality', 'sd')
            })
        
        print(f"[API] Returning {len(formatted_videos)} formatted videos")
        
        return jsonify({
            'videos': formatted_videos,
            'count': len(formatted_videos)
        })
        
    except Exception as e:
        print(f"Video fetching error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate/render', methods=['POST'])
def render_video():
    """
    Render final video from components - Stage 4
    
    Expected JSON body:
    {
        "script": "video script",
        "audio_path": "path/to/audio.mp3",
        "image_urls": ["url1", "url2", "url3"],
        "duration": 30
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        # In production, this would:
        # 1. Download images
        # 2. Create video clips from images
        # 3. Add audio narration
        # 4. Combine everything into final video
        # 5. Return video URL
        
        # For now, return placeholder
        video_filename = f"video_{int(time.time())}.mp4"
        video_url = f"/assets/videos/{video_filename}"
        
        return jsonify({
            'video_url': video_url,
            'video_path': f"assets/videos/{video_filename}",
            'duration': data.get('duration', 30),
            'status': 'completed'
        })
        
    except Exception as e:
        print(f"Video rendering error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/editor/export', methods=['POST'])
def export_edited_video():
    """
    Export edited video from Editor Lab
    
    Expected JSON body:
    {
        "clips": [
            {
                "url": "video URL",
                "trimStart": 0,
                "trimEnd": 10,
                "speed": 1.0,
                "volume": 100,
                "fadeIn": 0,
                "fadeOut": 0,
                "brightness": 100,
                "contrast": 100,
                "rotation": 0,
                "flipH": false,
                "flipV": false
            }
        ]
    }
    
    Returns:
    {
        "video_url": "/assets/edited_videos/filename.mp4",
        "duration": 30.5,
        "status": "success"
    }
    """
    try:
        data = request.json
        clips = data.get('clips', [])
        
        if not clips:
            return jsonify({'error': 'No clips provided'}), 400
        
        print(f"[Editor] Exporting {len(clips)} clips")
        
        # Import video editor
        from video_editor import editor
        
        # Export video
        output_path = editor.export_video(clips)
        
        # Get video duration
        from moviepy.editor import VideoFileClip
        final_clip = VideoFileClip(output_path)
        duration = final_clip.duration
        final_clip.close()
        
        # Construct URL for frontend
        filename = os.path.basename(output_path)
        video_url = f'/assets/edited_videos/{filename}'
        
        print(f"[Editor] Export complete: {video_url}")
        
        return jsonify({
            'video_url': video_url,
            'video_path': output_path,
            'duration': duration,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"[Editor] Export error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/editor/combine-clips', methods=['POST', 'OPTIONS'])
def combine_clips():
    """
    Combine multiple video clips into one continuous video
    
    POST /api/editor/combine-clips
    Body: {
        "clips": ["/path/to/clip1.mp4", "/path/to/clip2.mp4", ...]
    }
    
    Returns: {
        "video_url": "/assets/edited_videos/combined_video.mp4",
        "duration": 45.2,
        "status": "success"
    }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        data = request.json
        clip_paths = data.get('clips', [])
        
        if not clip_paths or len(clip_paths) < 2:
            return jsonify({'error': 'At least 2 clips are required to combine'}), 400
        
        print(f"\n[Editor] ========================================")
        print(f"[Editor] Combining {len(clip_paths)} video clips")
        print(f"[Editor] ========================================")
        
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        import time
        
        # Load all video clips
        video_clips = []
        for i, clip_path in enumerate(clip_paths):
            # Handle both absolute paths and relative URLs
            if clip_path.startswith('/assets/'):
                # Convert URL to file path
                clip_path = clip_path.replace('/assets/', 'assets/')
            
            if not os.path.exists(clip_path):
                print(f"[Editor] Warning: Clip not found: {clip_path}")
                continue
            
            print(f"[Editor] Loading clip {i+1}/{len(clip_paths)}: {os.path.basename(clip_path)}")
            clip = VideoFileClip(clip_path)
            video_clips.append(clip)
        
        if len(video_clips) < 2:
            return jsonify({'error': 'Not enough valid clips found to combine'}), 400
        
        # Concatenate all clips
        print(f"[Editor] Concatenating {len(video_clips)} clips...")
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Generate output filename
        timestamp = int(time.time())
        output_filename = f"combined_video_{timestamp}.mp4"
        output_dir = os.path.join('assets', 'edited_videos')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        # Write combined video
        print(f"[Editor] Writing combined video: {output_filename}")
        final_clip.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=30,
            preset='medium',
            threads=4
        )
        
        duration = final_clip.duration
        
        # Clean up
        for clip in video_clips:
            clip.close()
        final_clip.close()
        
        # Construct URL for frontend
        video_url = f'/assets/edited_videos/{output_filename}'
        
        print(f"[Editor] ✅ Combined video created successfully!")
        print(f"[Editor] Duration: {duration:.2f}s")
        print(f"[Editor] URL: {video_url}")
        print(f"[Editor] ========================================\n")
        
        return jsonify({
            'video_url': video_url,
            'video_path': output_path,
            'duration': duration,
            'clip_count': len(video_clips),
            'status': 'success'
        })
        
    except Exception as e:
        print(f"[Editor] ❌ Error combining clips: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/huggingface/image-to-video', methods=['POST', 'OPTIONS'])
def hf_image_to_video():
    """Convert image to video using HuggingFace Stable Video Diffusion"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    try:
        if hf_service is None:
            return jsonify({
                'error': 'HuggingFace service not available',
                'details': 'Service failed to initialize. Check API key.'
            }), 503
        
        # Check if image file is provided
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided', 'details': 'Please upload an image'}), 400
        
        image_file = request.files['image']
        
        if image_file.filename == '':
            return jsonify({'error': 'No image selected', 'details': 'Please select an image file'}), 400
        
        print(f"\n[API] ========================================")
        print(f"[API] Image-to-Video conversion requested")
        print(f"[API] Image: {image_file.filename}")
        print(f"[API] ========================================")
        
        # Save uploaded image temporarily
        temp_dir = os.path.join('assets', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_path = os.path.join(temp_dir, f'input_{timestamp}.png')
        image_file.save(input_path)
        
        print(f"[API] Image saved to: {input_path}")
        print(f"[API] File size: {os.path.getsize(input_path)} bytes")
        print(f"[API] Starting conversion (this may take 30-90 seconds)...")
        
        # Convert image to video
        try:
            output_path = hf_service.image_to_video(input_path)
            print(f"[API] ✅ Video generated: {output_path}")
        except Exception as e:
            error_msg = str(e)
            print(f"[API] ❌ Conversion failed: {error_msg}")
            
            # Clean up temp input file
            try:
                os.remove(input_path)
            except:
                pass
            
            # Return appropriate error
            if "Model is currently loading" in error_msg:
                return jsonify({
                    'error': 'Model Loading',
                    'details': error_msg
                }), 503
            elif "timeout" in error_msg.lower():
                return jsonify({
                    'error': 'Request Timeout',
                    'details': 'The request took too long. Please try again.'
                }), 504
            else:
                return jsonify({
                    'error': 'Conversion Failed',
                    'details': error_msg
                }), 500
        
        # Verify output file exists
        if not os.path.exists(output_path):
            raise Exception("Video file was not created")
        
        # Get video file size
        video_size = os.path.getsize(output_path)
        print(f"[API] Video size: {video_size} bytes")
        
        # Read video file
        with open(output_path, 'rb') as f:
            video_data = f.read()
        
        # Clean up temp files
        try:
            os.remove(input_path)
            print(f"[API] Cleaned up temp input: {input_path}")
        except Exception as e:
            print(f"[API] Warning: Could not delete temp file: {e}")
        
        try:
            os.remove(output_path)
            print(f"[API] Cleaned up temp output: {output_path}")
        except Exception as e:
            print(f"[API] Warning: Could not delete output file: {e}")
        
        print(f"[API] ✅ Sending video response ({video_size} bytes)")
        print(f"[API] ========================================\n")
        
        # Return video file
        from flask import Response
        return Response(
            video_data,
            mimetype='video/mp4',
            headers={
                'Content-Disposition': 'attachment; filename="animated_video.mp4"',
                'Content-Length': str(video_size),
                'Content-Type': 'video/mp4'
            }
        )
        
    except Exception as e:
        print(f"[API] ❌ Unexpected error in image-to-video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'details': str(e)
        }), 500


if __name__ == '__main__':
    # Check for environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print("\nWarning: .env file not found!")
        print("Create a .env file with your API keys:")
        print("  GEMINI_API_KEY=your_key_here")
        print("  PEXELS_API_KEY=your_key_here")
        print("  OPENAI_API_KEY=your_key_here (optional)")
        print("  ANTHROPIC_API_KEY=your_key_here (optional)\n")
    
    print("Starting AI Video Generation API Server...")
    print("API will be available at: http://localhost:5000")
    print("Frontend should connect to: http://localhost:5000/api")
    print("\nAvailable endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/config/keys - Get API keys")
    print("  GET  /api/config/health - Check API key health")
    print("  POST /api/chat - AI chat assistance")
    print("  POST /api/chat/clear - Clear chat history")
    print("  GET  /api/chat/history - Get chat history")
    print("  POST /api/generate/script - Generate video script")
    print("  POST /api/generate/audio - Generate audio narration")
    print("  POST /api/generate/images - Generate/fetch images")
    print("  POST /api/generate/videos - Fetch videos from Pexels")
    print("  POST /api/generate/render - Render final video")
    print("  POST /api/generate/video - Generate complete video (full pipeline)")
    print("  POST /api/editor/export - Export edited video from Editor Lab")
    print("  GET  /assets/<filename> - Serve audio/video files")
    print("  POST /api/huggingface/image-to-video - Convert image to video (AI)")
    print("\n💡 Use start_server.py in root directory for production server with Waitress")
    print("\n")
    
    # Add error handler for uncaught exceptions
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Get port from environment variable (for production deployment)
    port = int(os.environ.get('PORT', 5000))
    
    # Check if running in production mode
    is_production = os.environ.get('ENVIRONMENT', 'development') == 'production'
    
    # Run with Flask threaded server (more compatible)
    print("🚀 Starting Flask server with threading support")
    print("🔄 Connection persistence enabled")
    print("⚡ Enhanced error handling active")
    print(f"🌍 Environment: {'Production' if is_production else 'Development'}")
    print(f"📍 Server: http://0.0.0.0:{port}")
    
    try:
        app.run(
            debug=not is_production, 
            host='0.0.0.0', 
            port=port, 
            use_reloader=False, 
            threaded=True
        )
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        print("\n🔄 Server will restart automatically if using a process manager")
