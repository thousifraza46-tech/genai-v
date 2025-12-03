"""
Production Backend Server Starter with Waitress
"""
import sys
import os

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

if __name__ == '__main__':
    print("🚀 Starting Production Backend Server with Waitress")
    print("📡 Server: http://localhost:5000")
    print("🔗 API Base: http://localhost:5000/api")
    print("⚡ Using production WSGI server (Waitress)")
    print("🔄 Auto-restart: Disabled")
    print("⏱️  Timeout: 300 seconds")
    print("\n✅ Starting...\n")
    
    try:
        from waitress import serve
        from api_server import app
        
        # Run with Waitress (production WSGI server)
        serve(
            app, 
            host='0.0.0.0', 
            port=5000,
            threads=6,  # Handle multiple concurrent requests
            channel_timeout=300,  # 5 minute timeout for long requests
            cleanup_interval=30,  # Clean up dead threads every 30s
            asyncore_use_poll=True  # Better performance on Windows
        )
    except ImportError:
        print("⚠️  Waitress not found, falling back to Flask development server")
        print("💡 Install Waitress for production: pip install waitress")
        from api_server import app
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False, threaded=True)
