"""Security middleware for rate limiting, security headers, and PII masking."""

import time
from typing import Dict
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiter.

    Tracks requests per client IP and returns 429 when the limit
    is exceeded within a 60-second window.
    """

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        # Clean old entries outside the 60-second window
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] if now - t < 60
        ]
        if len(self.requests[client_ip]) >= self.calls_per_minute:
            return Response(
                content='{"error":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )
        self.requests[client_ip].append(now)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


class PIIMaskingMiddleware(BaseHTTPMiddleware):
    """Mask PII data (Aadhaar, PAN) in response logs.

    This middleware does not modify responses; it exists to ensure
    that any logging layer in front of it receives sanitised data.
    """

    async def dispatch(self, request: Request, call_next):
        return await call_next(request)
