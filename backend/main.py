from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from backend.middleware.tracing import RequestTracerMiddleware
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.api.v1 import router as api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autergo API", version="1.0.0")

# 1. CORS middleware for local Vite dev server and production clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Rate limiting middleware
app.add_middleware(RateLimitMiddleware, max_requests_per_minute=200)

# 3. OpenTelemetry request tracing middleware
app.add_middleware(RequestTracerMiddleware)

# 4. API V1 Routes
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Prometheus scrape endpoint for OpenTelemetry / Grafana observability."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Mount React built assets
dist_assets = os.path.join("frontend", "dist", "assets")
if os.path.exists(dist_assets):
    app.mount("/assets", StaticFiles(directory=dist_assets), name="assets")

# Single Page Application (SPA) fallback route for React Router
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    if full_path.startswith("api") or full_path.startswith("health") or full_path.startswith("metrics"):
        raise HTTPException(status_code=404, detail="Not Found")
    
    dist_dir = os.path.join("frontend", "dist")
    file_path = os.path.join(dist_dir, full_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    index_path = os.path.join(dist_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "Autergo API is running. React frontend available in frontend/"}
