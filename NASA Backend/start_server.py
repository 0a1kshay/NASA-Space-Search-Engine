#!/usr/bin/env python3
"""
Simple startup script to test the NASA Space Biology API
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        import uvicorn
        from main import app
        
        print("🚀 Starting NASA Space Biology API...")
        print("📍 Server will be available at: http://127.0.0.1:8000")
        print("📚 API Documentation: http://127.0.0.1:8000/docs")
        print("🏥 Health Check: http://127.0.0.1:8000/health")
        print()
        
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install required packages:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)