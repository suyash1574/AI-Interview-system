from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import logging
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram, Gauge

from backend.middleware.tracing import RequestTracerMiddleware
from backend.middleware.rate_limit import RateLimitMiddleware
from backend.api.v1 import router as api_v1_router
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom Prometheus observability metrics for the real-time AI interview pipeline
STT_LATENCY_HISTOGRAM = Histogram(
    "autergo_stt_duration_seconds", 
    "STT audio transcription latency in seconds", 
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)
LLM_LATENCY_HISTOGRAM = Histogram(
    "autergo_llm_duration_seconds", 
    "LLM completion latency in seconds", 
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 3.0, 5.0]
)
TTS_LATENCY_HISTOGRAM = Histogram(
    "autergo_tts_duration_seconds", 
    "TTS synthesis latency in seconds", 
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
)
ACTIVE_INTERVIEWS_GAUGE = Gauge(
    "autergo_active_interviews", 
    "Number of currently active live interviews"
)
INTERVIEWS_COMPLETED_TOTAL = Counter(
    "autergo_interviews_completed_total", 
    "Total completed interviews"
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Fail-fast startup configuration check.
    In production mode (ENV == 'production'), asserts presence of mandatory credentials.
    In development / test modes, logs warnings and permits fallback adapters.
    """
    if settings.ENV.lower() == "production":
        missing_keys = []
        if not settings.CLERK_SECRET_KEY:
            missing_keys.append("CLERK_SECRET_KEY")
        if not (settings.GROQ_API_KEY or settings.NVIDIA_API_KEY):
            missing_keys.append("GROQ_API_KEY or NVIDIA_API_KEY")
        if not (settings.DEEPGRAM_API_KEY or settings.HF_API_TOKEN):
            missing_keys.append("DEEPGRAM_API_KEY or HF_API_TOKEN")
        if missing_keys:
            raise RuntimeError(
                f"Production startup validation failed: Mandatory environment variables missing: {', '.join(missing_keys)}"
            )
    logger.info(f"Autergo API started successfully in {settings.ENV} mode.")
    yield

app = FastAPI(title="Autergo API", version="1.0.0", lifespan=lifespan)



# 1. CORS middleware for local Vite dev server and production clients
allowed_origins_list = (
    [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    if settings.ALLOWED_ORIGINS and settings.ALLOWED_ORIGINS != "*"
    else ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins_list,
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
