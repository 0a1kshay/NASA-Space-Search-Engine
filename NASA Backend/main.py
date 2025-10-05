from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routers
from app.routers import search, graph, summarize, compare, ingest

# Try to import lightweight CSV service first, fallback to pandas version
try:
    from app.csv_service_lightweight import csv_service
    logger.info("Using lightweight CSV service (no pandas)")
except ImportError:
    from app.csv_service import csv_service
    logger.info("Using pandas CSV service")

app = FastAPI(
    title="NASA Space Biology Knowledge Engine API",
    description="API for NASA space biology publications and knowledge graph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite dev server (alternate port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:4173",  # Vite preview
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "x-api-key",
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
)

# Include API routers
app.include_router(search.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(summarize.router, prefix="/api")
app.include_router(compare.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Startup event to load CSV data
@app.on_event("startup")
async def startup_event():
    """Load CSV data on application startup"""
    logger.info("Loading CSV data on startup...")
    success = csv_service.load_csv_data()
    if success:
        stats = csv_service.get_stats()
        logger.info(f"CSV data loaded: {stats['total_articles']} articles from {stats['csv_path']}")
    else:
        logger.warning("Failed to load CSV data - search will return empty results")

# Serve favicon.ico
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "NASA Space Biology API"}

# Serve main page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NASA Space Biology API</title>
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>NASA Space Biology Knowledge Engine API</h1>
        <p>🚀 Backend server is running successfully!</p>
        
        <h2>Available Endpoints:</h2>
        <div class="endpoint"><strong>GET /api/graph</strong> - Get knowledge graph data</div>
        <div class="endpoint"><strong>GET /api/graph/node/{id}</strong> - Get detailed node information</div>
        <div class="endpoint"><strong>GET /api/search?query=...</strong> - Search publications</div>
        <div class="endpoint"><strong>POST /api/summarize</strong> - Generate AI summary</div>
        <div class="endpoint"><strong>POST /api/compare</strong> - Compare publications</div>
        <div class="endpoint"><strong>POST /api/ingest</strong> - Add new publication</div>
        
        <h2>Documentation:</h2>
        <p><a href="/docs">📚 Swagger UI Documentation</a></p>
        <p><a href="/redoc">📖 ReDoc Documentation</a></p>
        
        <h2>Health Check:</h2>
        <p><a href="/health">🏥 API Health Status</a></p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)