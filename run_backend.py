# -*- coding: utf-8 -*-
"""
Backend Server Launcher - Runs as independent background process
Double-click this file or run: python run_backend.py
"""
import sys
import os
import subprocess
import time
import requests

def check_server_running():
    """Check if server is already running"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start server as detached background process"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    server_script = os.path.join(backend_dir, 'stable_server.py')
    
    print("=" * 60)
    print("Backend Server Launcher")
    print("=" * 60)
    print()
    
    # Check if already running
    if check_server_running():
        print("[INFO] Backend server is already running!")
        print("[URL] http://localhost:5000")
        print()
        input("Press Enter to exit...")
        return
    
    print("[START] Launching backend server...")
    print("[INFO] Server will run independently in background")
    print()
    
    # Start server as detached process (no window, independent)
    if sys.platform == 'win32':
        # Windows: Use CREATE_NO_WINDOW flag
        DETACHED_PROCESS = 0x00000008
        CREATE_NO_WINDOW = 0x08000000
        
        subprocess.Popen(
            [sys.executable, server_script],
            cwd=backend_dir,
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
    else:
        # Linux/Mac: Fork and detach
        subprocess.Popen(
            [sys.executable, server_script],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
    
    # Wait for server to start
    print("[WAIT] Waiting for server to initialize...")
    for i in range(10):
        time.sleep(1)
        if check_server_running():
            print()
            print("=" * 60)
            print("SUCCESS! Backend Server Running")
            print("=" * 60)
            print(f"URL:    http://localhost:5000")
            print(f"API:    http://localhost:5000/api")
            print(f"Status: http://localhost:5000/api/health")
            print()
            print("The server is running in the background.")
            print("You can close this window safely.")
            print()
            print("To stop: Run STOP_BACKEND.bat")
            print("=" * 60)
            print()
            input("Press Enter to exit...")
            return
    
    print()
    print("[ERROR] Server did not start within 10 seconds")
    print("[HELP] Try running START_BACKEND.bat to see error messages")
    print()
    input("Press Enter to exit...")

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n[STOP] Cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
