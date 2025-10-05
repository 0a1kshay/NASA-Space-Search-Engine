"""
Vercel API Entry Point for NASA Space Biology Knowledge Engine
This file serves as the entry point for Vercel deployment
"""

import sys
import os
from pathlib import Path

# Add the NASA Backend directory to Python path
backend_dir = Path(__file__).parent / "NASA Backend"
sys.path.insert(0, str(backend_dir))

# Change working directory to NASA Backend
os.chdir(str(backend_dir))

# Import the FastAPI app from main.py
from main import app

# This is the entry point that Vercel will use
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)