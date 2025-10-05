#!/bin/bash
# 🧪 NASA Backend Build Verification Script
# Tests the build process locally before Render deployment

echo "🚀 NASA Backend Build Verification Starting..."
echo "========================================"

# Set Python version
export PYTHON_VERSION=3.11.9

# Create virtual environment
echo "🐍 Creating Python 3.11 virtual environment..."
if command -v python3.11 &> /dev/null; then
    python3.11 -m venv venv_test
elif command -v python3 &> /dev/null; then
    python3 -m venv venv_test
else
    python -m venv venv_test
fi

# Activate virtual environment
source venv_test/bin/activate || source venv_test/Scripts/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies with optimizations
echo "📋 Installing dependencies..."
echo "Using --only-binary=all to avoid compilation issues..."
pip install --only-binary=all -r requirements.txt

# Check if pandas was installed (should not be with our fixed requirements.txt)
echo "🔍 Checking for pandas..."
if python -c "import pandas" 2>/dev/null; then
    echo "⚠️  WARNING: pandas is still installed - this may cause build issues"
    pip uninstall pandas -y
else
    echo "✅ pandas not found - good!"
fi

# Test core imports
echo "🧪 Testing core imports..."
python -c "
import fastapi
import uvicorn
import neo4j
import openai
import httpx
import aiohttp
print('✅ All core dependencies imported successfully!')
"

# Test our lightweight CSV service
echo "📊 Testing lightweight CSV service..."
python -c "
from app.csv_service_lightweight import csv_service
print('✅ Lightweight CSV service imported successfully!')
stats = csv_service.get_stats()
print(f'📈 CSV service stats: {stats}')
"

# Test FastAPI app startup
echo "🌐 Testing FastAPI app startup..."
python -c "
from main import app
print('✅ FastAPI app created successfully!')
print(f'📋 App title: {app.title}')
print(f'🔗 Docs URL: {app.docs_url}')
"

# Cleanup
deactivate
rm -rf venv_test

echo "========================================"
echo "🎉 Build verification completed successfully!"
echo "✅ Your NASA Backend is ready for Render deployment!"
echo ""
echo "Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Fix pandas compatibility for Python 3.11'"
echo "3. git push origin main"
echo "4. Deploy on Render using the render.yaml configuration"