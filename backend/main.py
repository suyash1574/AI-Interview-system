from fastapi import FastAPI, Request
import uuid
import logging
from backend.middleware.tracing import RequestTracerMiddleware
from backend.api.v1 import router as api_v1_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Autergo API", version="1.0.0")

app.add_middleware(RequestTracerMiddleware)
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
