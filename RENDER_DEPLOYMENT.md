# NASA Space Biology Knowledge Engine - Render Deployment Guide

## 🚀 Complete Deployment Guide for Render.com

This guide will walk you through deploying both the React frontend and FastAPI backend to Render.com.

### 📋 Prerequisites

1. **GitHub Repository**: Your code must be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Neo4j Database**: You'll need Neo4j credentials (URI, username, password)
4. **OpenAI API Key** (optional): For AI summarization features

### 🏗️ Project Structure

```
NASA/
├── render.yaml                 # Render configuration
├── NASA Backend/              # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── app/
└── NASA Frontend/             # React frontend
    ├── package.json
    ├── vite.config.ts
    ├── .env.production
    └── src/
```

## 📥 Step-by-Step Deployment

### Step 1: Push to GitHub

1. Ensure all your code is committed and pushed to GitHub:
```bash
git add .
git commit -m "Configure for Render deployment"
git push origin main
```

### Step 2: Deploy via render.yaml (Recommended)

1. **Login to Render**: Go to [render.com](https://render.com) and sign in
2. **New Blueprint**: Click "New +" → "Blueprint"
3. **Connect Repository**: Select your GitHub repository
4. **Configure Services**: Render will automatically detect the `render.yaml` file

### Step 3: Set Environment Variables

**For nasa-backend service:**
- `NEO4J_URI`: Your Neo4j database URI (e.g., `neo4j+s://xxx.databases.neo4j.io`)
- `NEO4J_USER`: Your Neo4j username (usually `neo4j`)
- `NEO4J_PASSWORD`: Your Neo4j password
- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `FRONTEND_URL`: Will be auto-set to your frontend URL

**For nasa-frontend service:**
- `VITE_API_URL`: Will be auto-set to your backend URL
- Environment variables are automatically configured via render.yaml

### Step 4: Manual Deployment (Alternative)

If you prefer manual setup:

#### Backend Service:
1. **New Web Service** → Connect your repository
2. **Settings**:
   - Name: `nasa-backend`
   - Runtime: `Python 3`
   - Build Command: `cd 'NASA Backend' && pip install -r requirements.txt`
   - Start Command: `cd 'NASA Backend' && python -m uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`

#### Frontend Service:
1. **New Static Site** → Connect your repository
2. **Settings**:
   - Name: `nasa-frontend`
   - Build Command: `cd 'NASA Frontend' && npm ci && npm run build`
   - Publish Directory: `NASA Frontend/dist`
   - Rewrite Rules: `/*` → `/index.html`

## 🔧 Configuration Details

### Backend Configuration

The backend is configured with:
- **CORS**: Automatically includes your frontend URL
- **Health Check**: Available at `/health`
- **API Documentation**: Available at `/docs` after deployment
- **Environment Detection**: Automatically switches between dev/prod settings

### Frontend Configuration

The frontend is configured with:
- **Environment Variables**: Automatically uses production API URL
- **React Router**: All routes properly rewritten to `/index.html`
- **Build Optimization**: Code splitting and vendor chunking
- **Static Asset Serving**: All assets properly served from `/assets/`

### Database Configuration

**Neo4j Setup** (if you don't have one):
1. Go to [neo4j.com/aura](https://neo4j.com/aura)
2. Create a free AuraDB instance
3. Note down the URI, username, and password
4. Add these to your Render environment variables

## ✅ Deployment Verification

### Step 1: Check Backend Health
```bash
curl https://your-backend-url.onrender.com/health
```
Expected response:
```json
{"status": "healthy", "service": "NASA Space Biology API"}
```

### Step 2: Test API Documentation
Visit: `https://your-backend-url.onrender.com/docs`

### Step 3: Verify Frontend
1. Visit your frontend URL
2. Check that the homepage loads
3. Test search functionality
4. Verify API calls in browser dev tools

### Step 4: Test Full Integration
1. Navigate to the search page
2. Enter a search query (e.g., "microgravity")
3. Verify results are returned
4. Check browser console for any errors

## 🐛 Troubleshooting

### Common Issues:

**1. Backend Won't Start**
- Check build logs for Python errors
- Verify `requirements.txt` is correct
- Ensure `main.py` is in the root of `NASA Backend/`

**2. Frontend Shows API Errors**
- Verify `VITE_API_URL` environment variable
- Check CORS settings in backend
- Confirm backend is running and healthy

**3. Database Connection Issues**
- Verify Neo4j credentials in environment variables
- Check Neo4j instance is running and accessible
- Test connection from backend logs

**4. 404 Errors on Frontend Routes**
- Ensure rewrite rules are set: `/*` → `/index.html`
- Check that build output is in correct directory

### Debugging Commands:

**View Render Logs:**
```bash
# Install Render CLI
npm install -g render-cli

# View backend logs
render logs -s nasa-backend

# View frontend build logs
render logs -s nasa-frontend
```

**Local Testing:**
```bash
# Test backend locally
cd "NASA Backend"
uvicorn main:app --reload

# Test frontend locally
cd "NASA Frontend"
npm run dev
```

## 🔄 Continuous Deployment

Once set up, Render will automatically:
1. **Auto-deploy** on every push to your main branch
2. **Run builds** for both frontend and backend
3. **Update environment variables** as configured
4. **Health check** services after deployment

## 📊 Monitoring

**Render Dashboard:**
- Service health and uptime
- Build and deployment logs
- Performance metrics
- Custom domain setup

**Application Monitoring:**
- Backend: `/health` endpoint
- Frontend: Browser console and network tab
- Database: Neo4j browser or monitoring tools

## 🔗 URLs After Deployment

- **Backend API**: `https://nasa-backend.onrender.com`
- **Frontend App**: `https://nasa-frontend.onrender.com`
- **API Docs**: `https://nasa-backend.onrender.com/docs`
- **Health Check**: `https://nasa-backend.onrender.com/health`

## 💡 Production Optimizations

**Backend:**
- Gunicorn for production WSGI server
- Database connection pooling
- Caching for frequently accessed data
- Rate limiting and authentication

**Frontend:**
- CDN for static assets
- Gzip compression
- Bundle size optimization
- Service worker for offline capability

**Database:**
- Neo4j production instance
- Regular backups
- Query optimization
- Index management

## 🎉 Success!

Your NASA Space Biology Knowledge Engine is now live on Render! 

- Share your app: `https://nasa-frontend.onrender.com`
- Monitor health: `https://nasa-backend.onrender.com/health`
- API docs: `https://nasa-backend.onrender.com/docs`

Happy exploring! 🚀🌌