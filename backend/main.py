from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uuid
import logging
from backend.middleware.tracing import RequestTracerMiddleware
from backend.api.v1 import router as api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autergo API", version="1.0.0")

app.add_middleware(RequestTracerMiddleware)
app.include_router(api_v1_router, prefix="/api/v1")

# Mount frontend directory for static UI assets and pages
if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Autergo API is running. Visit /frontend/ or /api/v1/docs"}
