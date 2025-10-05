"""
Alternative entry point - index.py at root level
"""

import sys
import os
from pathlib import Path

# Add the NASA Backend directory to Python path
backend_dir = Path(__file__).parent / "NASA Backend"
sys.path.insert(0, str(backend_dir))

# Change working directory to NASA Backend
os.chdir(str(backend_dir))

# Import the FastAPI app from NASA Backend/main.py
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("backend_main", str(backend_dir / "main.py"))
backend_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend_main)
app = backend_main.app

# Export the app for Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)