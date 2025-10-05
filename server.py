"""
Server entry point for Vercel deployment
"""

import sys
import os
from pathlib import Path

# Set up paths
current_dir = Path(__file__).parent
backend_dir = current_dir / "NASA Backend"

# Add backend to Python path
sys.path.insert(0, str(backend_dir))

# Change to backend directory for relative imports
original_cwd = os.getcwd()
os.chdir(str(backend_dir))

try:
    # Import the FastAPI app from NASA Backend
    import main as backend_main
    app = backend_main.app
    
    # Restore original directory
    os.chdir(original_cwd)
    
except Exception as e:
    os.chdir(original_cwd)
    raise e

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)