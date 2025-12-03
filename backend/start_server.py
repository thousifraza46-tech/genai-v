"""
Backend Server Startup Script
Tests connections and starts the Flask API server
"""

import sys
import os
import subprocess

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_env_file():
    """Check if .env file exists"""
    print_header("CHECKING ENVIRONMENT")
    
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    if os.path.exists(env_path):
        print_success(".env file found")
        
        # Check for API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        gemini_key = os.getenv('GEMINI_API_KEY')
        pexels_key = os.getenv('PEXELS_API_KEY')
        
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            print_success("GEMINI_API_KEY configured")
        else:
            print_warning("GEMINI_API_KEY not configured (AI features limited)")
        
        if pexels_key and pexels_key != 'your_pexels_api_key_here':
            print_success("PEXELS_API_KEY configured")
        else:
            print_warning("PEXELS_API_KEY not configured (image search limited)")
        
        return True
    else:
        print_error(".env file not found!")
        print_info("Copy .env.example to .env and add your API keys")
        return False

def quick_test_modules():
    """Quick test of critical modules"""
    print_header("TESTING BACKEND MODULES")
    
    try:
        # Test Flask imports
        import flask
        import flask_cors
        print_success("Flask and CORS installed")
        
        # Test AI modules
        try:
            import google.generativeai
            print_success("Google Gemini AI available")
        except ImportError:
            print_warning("Google Gemini AI not available")
        
        # Test audio generation
        try:
            import edge_tts
            print_success("Edge TTS (audio generation) available")
        except ImportError:
            print_warning("Edge TTS not available")
        
        # Test video processing
        try:
            import moviepy
            print_success("MoviePy (video processing) available")
        except ImportError:
            print_warning("MoviePy not available")
        
        # Test backend modules
        sys.path.append(os.path.dirname(__file__))
        
        from chatbot_engine import generate_chatbot_response
        print_success("Chatbot engine loaded")
        
        from script_generator import ScriptGenerator
        print_success("Script generator loaded")
        
        from audio_generator import AudioGenerator
        print_success("Audio generator loaded")
        
        from pexels_video_generator import PexelsVideoGenerator
        print_success("Image generator loaded")
        
        from scene_builder import combine_videos
        print_success("Scene builder loaded")
        
        return True
        
    except Exception as e:
        print_error(f"Module test failed: {e}")
        return False

def start_server():
    """Start the Flask API server"""
    print_header("STARTING API SERVER")
    
    print_info("Flask server will start on http://localhost:5000")
    print_info("Press Ctrl+C to stop the server\n")
    
    try:
        # Import and run the server
        from api_server import app
        
        print(f"{Colors.GREEN}{Colors.BOLD}")
        print("🚀 API SERVER RUNNING")
        print("=" * 60)
        print("📡 Backend API: http://localhost:5000")
        print("🔗 API Endpoints: http://localhost:5000/api")
        print("📖 Health Check: http://localhost:5000/api/health")
        print("=" * 60)
        print(f"{Colors.RESET}\n")
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⏹️  Server stopped by user{Colors.RESET}")
    except Exception as e:
        print_error(f"Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main startup routine"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'='*58}╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{' '*58}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{'🎬 AI VIDEO GENERATION - BACKEND SERVER 🎬'.center(58)}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{' '*58}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚{'='*58}╝{Colors.RESET}\n")
    
    # Step 1: Check environment
    env_ok = check_env_file()
    if not env_ok:
        print_warning("Continuing without .env file (limited functionality)\n")
    
    # Step 2: Quick module test
    modules_ok = quick_test_modules()
    if not modules_ok:
        print_error("Module tests failed. Please check your installation.")
        print_info("Run: pip install -r ../requirements.txt")
        sys.exit(1)
    
    # Step 3: Start server
    print_success("All checks passed!\n")
    start_server()

if __name__ == "__main__":
    main()
