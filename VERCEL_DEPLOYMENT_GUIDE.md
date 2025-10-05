# Vercel Deployment Guide for NASA Space Biology API

## Overview
This guide will help you deploy your FastAPI backend to Vercel with proper entrypoint detection.

## Files Created for Vercel Deployment:

### 1. `vercel.json` - Vercel Configuration
- Specifies multiple entry points (`main.py`, `index.py`, `server.py`)
- Configures Python 3.11 runtime
- Sets up routing to handle all requests
- Includes NASA Backend files in the deployment

### 2. Multiple Entry Points Created:
- `main.py` - Primary entry point (Vercel looks for this first)
- `index.py` - Alternative entry point 
- `server.py` - Server entry point
- `api.py` - API entry point
All handle path setup and import the FastAPI app from `NASA Backend/main.py`

### 3. `requirements.txt` - Root Level Dependencies
- Pandas-free version for better Vercel compatibility
- Contains all necessary FastAPI and API dependencies

### 4. `csv_service_lightweight.py` - Pandas-Free CSV Service
- Uses pure Python instead of pandas
- Compatible with serverless deployment
- Maintains the same API as the original service

### 5. Fixed Import Issues:
- Resolved circular import problems
- Fixed logger initialization order in `NASA Backend/main.py`
- Proper module loading to avoid naming conflicts

## Deployment Steps:

### 1. Prepare Your Repository
```bash
# Make sure all files are committed
git add .
git commit -m "Add Vercel deployment configuration"
git push
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI if you haven't already
npm i -g vercel

# Deploy from the root directory
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Choose your account
# - Link to existing project? No (for first deployment)
# - What's your project's name? nasa-space-biology-api
# - In which directory is your code located? ./
```

#### Option B: Using Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Import your Git repository
4. Set the following configuration:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: pip install -r requirements.txt

### 3. Configure Environment Variables
In the Vercel dashboard, go to your project > Settings > Environment Variables and add:

```
OPENAI_API_KEY=your_actual_openai_key
NEO4J_URI=your_neo4j_uri (if using)
NEO4J_USER=your_neo4j_user (if using)
NEO4J_PASSWORD=your_neo4j_password (if using)
MONGODB_URI=your_mongodb_uri (if using)
```

### 4. Update CORS Origins
In `NASA Backend/main.py`, add your Vercel domain to the CORS origins:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173", 
    "http://localhost:5174",
    "https://your-frontend-domain.vercel.app",  # Add your frontend domain
    "https://your-vercel-api-domain.vercel.app",  # Add your API domain
],
```

### 5. Test the Deployment
After deployment, test these endpoints:
- `https://your-app.vercel.app/health` - Health check
- `https://your-app.vercel.app/docs` - API documentation
- `https://your-app.vercel.app/api/search` - Search endpoint

## Project Structure for Vercel:
```
/
├── main.py               # Primary Vercel entry point ✅
├── index.py              # Alternative entry point ✅  
├── server.py             # Server entry point ✅
├── api.py                # API entry point ✅
├── requirements.txt      # Root level dependencies
├── vercel.json          # Vercel configuration
├── .env                 # Environment variables
└── NASA Backend/        # Your existing backend code
    ├── main.py          # FastAPI app (fixed logger issue)
    ├── requirements.txt # Backend dependencies (backup)
    └── app/
        ├── csv_service_lightweight.py  # Pandas-free service
        └── ...
```

## Key Changes Made:

1. **Removed pandas dependency** - Using pure Python CSV processing for better serverless compatibility
2. **Created root-level entry point** - `api.py` handles path setup and imports
3. **Updated main.py** - Now imports lightweight CSV service with fallback
4. **Proper Vercel configuration** - `vercel.json` with correct build settings

## Troubleshooting:

### If you get "No FastAPI entrypoint found":
- Make sure `api.py` is at the root level
- Check that `vercel.json` points to `api.py`
- Verify the `builds` section uses `@vercel/python`

### If you get import errors:
- Check that all dependencies are in the root `requirements.txt`
- Verify the `PYTHONPATH` is set correctly in `vercel.json`

### If CSV data doesn't load:
- Check that your data files are in `NASA Backend/data/`
- Verify the file paths in `csv_service_lightweight.py`
- Look at the Vercel function logs for specific errors

## Next Steps:
1. Deploy to Vercel using the steps above
2. Update your frontend API URL to point to the Vercel deployment
3. Test all endpoints to ensure everything works
4. Set up your custom domain if needed