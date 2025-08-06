
#!/usr/bin/env python3
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend server"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 Starting Backend Server...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Serve the frontend files"""
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    print("🌐 Starting Frontend Server...")
    try:
        subprocess.run([
            sys.executable, "-m", "http.server", 
            "3000", 
            "--bind", "0.0.0.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    print("🎯 Research Analyser - Starting Development Servers")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    print("🔗 Backend: http://0.0.0.0:8000")
    print("🔗 Frontend: http://0.0.0.0:3000")
    print("🔗 API Docs: http://0.0.0.0:8000/docs")
    print("=" * 50)
    
    try:
        # Run frontend in main thread
        run_frontend()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()
