#!/bin/bash

# Production startup script for NASA Backend on Render
echo "🚀 Starting NASA Space Biology API..."

# Set Python path
export PYTHONPATH="/opt/render/project/src/NASA Backend:$PYTHONPATH"

# Print environment info
echo "Environment: $ENVIRONMENT"
echo "Python path: $PYTHONPATH"
echo "Port: $PORT"

# Start the application
echo "🌐 Starting FastAPI server on port $PORT..."
cd "NASA Backend"
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --log-level info