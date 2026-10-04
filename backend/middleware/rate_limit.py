import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window in-memory rate limiter per IP/client identifier.
    Guards against abuse and brute-force attacks across API routes.
    """
    def __init__(self, app, max_requests_per_minute: int = 120):
        super().__init__(app)
        self.max_requests = max_requests_per_minute
        self.requests = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Allow static files and docs without rate limit
        path = request.url.path
        if path.startswith("/assets") or path in ["/docs", "/openapi.json", "/health", "/metrics"]:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - 60.0

        # Purge timestamps outside sliding window
        window = [t for t in self.requests[client_ip] if t > window_start]
        self.requests[client_ip] = window

        if len(window) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client {client_ip} on {path}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please wait before retrying.",
                    "retry_after_seconds": int(60 - (now - window[0])),
                },
                headers={"Retry-After": "60"}
            )

        self.requests[client_ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests - len(window) - 1))
        return response
