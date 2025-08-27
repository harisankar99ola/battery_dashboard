#!/usr/bin/env python3
"""
Battery Dashboard Application
============================

Main entry point for the Battery Data Analysis Dashboard.
This application provides a web-based interface for analyzing battery test data
stored in Google Drive.

Usage:
    python main.py

The application will start both the backend API server and frontend dashboard.
Access the dashboard at: http://localhost:8050

Requirements:
    - credentials.json file must be present in the project root
    - Python 3.8+
    - All dependencies from requirements.txt

Author: Battery Dashboard Team
Version: 1.0.0
"""

import sys
import subprocess
import threading
import time
import webbrowser
import socket
from pathlib import Path

# Add src directories to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir / "backend"
frontend_dir = current_dir / "frontend"

sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(frontend_dir))

# Global variables to store process references
backend_process = None
frontend_process = None

def cleanup_processes():
    """Cleanup backend and frontend processes."""
    global backend_process, frontend_process
    
    if backend_process and backend_process.poll() is None:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            try:
                backend_process.kill()
            except Exception:
                pass
    
    if frontend_process and frontend_process.poll() is None:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
        except (subprocess.TimeoutExpired, Exception):
            try:
                frontend_process.kill()
            except Exception:
                pass

def check_port(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False  # Port is available
        except OSError:
            return True   # Port is in use

def check_credentials():
    """Check if credentials.json exists in the project root."""
    credentials_path = current_dir.parent / "credentials.json"
    if not credentials_path.exists():
        print("❌ ERROR: credentials.json not found!")
        print("📁 Please place your Google Drive API credentials file at:")
        print(f"   {credentials_path}")
        print("\n📋 To get credentials.json:")
        print("   1. Go to Google Cloud Console")
        print("   2. Create a project and enable Google Drive API")
        print("   3. Create OAuth 2.0 credentials (Desktop application)")
        print("   4. Download as credentials.json")
        print("   5. Place in the project root directory")
        print("\n💡 You can run 'setup_credentials.bat' for detailed instructions")
        return False
    return True

def start_backend():
    """Start the FastAPI backend server using subprocess."""
    global backend_process
    print("🚀 Starting backend server...")
    
    if check_port(8000):
        print("⚠️  Port 8000 is already in use. Trying to continue...")
    
    try:
        # Use subprocess to start the backend
        backend_script = backend_dir / "main.py"
        if not backend_script.exists():
            backend_script = backend_dir / "main_simple.py"
        
        if not backend_script.exists():
            print(f"❌ Backend script not found in {backend_dir}")
            return False
            
        backend_process = subprocess.Popen([
            sys.executable, str(backend_script)
        ], cwd=str(backend_dir))
        
        # Wait a moment and check if process started
        time.sleep(2)
        if backend_process.poll() is None:
            print("✅ Backend server started on http://localhost:8000")
            return True
        else:
            print("❌ Backend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start the Dash frontend server using subprocess."""
    global frontend_process
    print("🌐 Starting frontend dashboard...")
    
    if check_port(8050):
        print("⚠️  Port 8050 is already in use. Trying to continue...")
    
    try:
        # Use subprocess to start the frontend  
        frontend_script = frontend_dir / "app.py"
        if not frontend_script.exists():
            print(f"❌ Frontend script not found: {frontend_script}")
            return False
            
        frontend_process = subprocess.Popen([
            sys.executable, str(frontend_script)
        ], cwd=str(frontend_dir))
        
        # Wait a moment and check if process started
        time.sleep(3)
        if frontend_process.poll() is None:
            print("✅ Frontend dashboard started on http://localhost:8050")
            return True
        else:
            print("❌ Frontend failed to start")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def main():
    """Main application entry point."""
    print("=" * 60)
    print("🔋 Battery Data Analysis Dashboard")
    print("=" * 60)
    
    # Check for credentials
    if not check_credentials():
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ Credentials found!")
    print("🔄 Starting application servers...")
    
    # Start backend
    if not start_backend():
        print("❌ Failed to start backend server")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Wait a moment for backend to stabilize
    time.sleep(2)
    
    # Start frontend
    if not start_frontend():
        print("❌ Failed to start frontend server")
        cleanup_processes()
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Wait for frontend to start
    time.sleep(3)
    
    # Open browser
    print("🌐 Opening browser...")
    try:
        webbrowser.open("http://localhost:8050")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("📱 Please manually open: http://localhost:8050")
    
    print("\n" + "=" * 60)
    print("✅ Battery Dashboard is running!")
    print("📊 Frontend: http://localhost:8050")
    print("🔌 Backend API: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("\n💡 Press Ctrl+C to stop the application")
    
    try:
        # Keep the main process alive
        while True:
            time.sleep(1)
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend process stopped unexpectedly")
                break
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend process stopped unexpectedly") 
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
    finally:
        cleanup_processes()
        print("✅ All services stopped. Goodbye!")

if __name__ == "__main__":
    main()
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a bit for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Wait a bit for frontend to start
    print("⏳ Waiting for frontend to initialize...")
    time.sleep(3)
    
    # Open browser
    print("🌐 Opening dashboard in browser...")
    webbrowser.open("http://localhost:8050")
    
    print("\n" + "=" * 60)
    print("✅ Battery Dashboard is now running!")
    print("📊 Frontend Dashboard: http://localhost:8050")
    print("🔌 Backend API: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    print("\n💡 Press Ctrl+C to stop the application")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Battery Dashboard...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
