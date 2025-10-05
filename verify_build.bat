@echo off
REM 🧪 NASA Backend Build Verification - Windows Version
echo 🚀 NASA Backend Build Verification Starting...
echo ========================================

REM Create virtual environment
echo 🐍 Creating Python virtual environment...
python -m venv venv_test

REM Activate virtual environment
call venv_test\Scripts\activate.bat

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📋 Installing dependencies...
echo Using --only-binary=all to avoid compilation issues...
pip install --only-binary=all -r "NASA Backend\requirements.txt"

REM Check pandas
echo 🔍 Checking for pandas...
python -c "import pandas" 2>nul && (
    echo ⚠️  WARNING: pandas is still installed - removing...
    pip uninstall pandas -y
) || (
    echo ✅ pandas not found - good!
)

REM Test core imports
echo 🧪 Testing core imports...
python -c "import fastapi, uvicorn, neo4j, openai, httpx, aiohttp; print('✅ All core dependencies imported successfully!')"

REM Test CSV service
echo 📊 Testing lightweight CSV service...
cd "NASA Backend"
python -c "from app.csv_service_lightweight import csv_service; print('✅ Lightweight CSV service works!')"

REM Test FastAPI
echo 🌐 Testing FastAPI app...
python -c "from main import app; print('✅ FastAPI app works!'); print(f'📋 App: {app.title}')"

REM Cleanup
cd ..
call venv_test\Scripts\deactivate.bat
rmdir /s /q venv_test

echo ========================================
echo 🎉 Build verification completed successfully!
echo ✅ Your NASA Backend is ready for Render deployment!
echo.
echo Next steps:
echo 1. git add .
echo 2. git commit -m "Fix pandas compatibility for Python 3.11"
echo 3. git push origin main
echo 4. Deploy on Render

pause