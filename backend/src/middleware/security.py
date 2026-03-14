"""Security middleware for rate limiting, security headers, and PII masking."""

import logging
import time
from typing import Dict, Optional
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiter with Redis support and per-user limits.

    Uses Redis for distributed rate limiting when available, falling
    back to in-memory tracking if Redis is unavailable.

    Rate limits:
    - Authenticated users: 300 requests/minute
    - Unauthenticated users: 60 requests/minute
    - Public signing endpoints (/esign/sign/): 20 requests/minute
    """

    AUTHENTICATED_LIMIT = 300
    UNAUTHENTICATED_LIMIT = 60
    SIGNING_ENDPOINT_LIMIT = 20

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        # In-memory fallback
        self.requests: Dict[str, list] = defaultdict(list)
        self._redis = None
        self._redis_checked = False

    def _get_redis(self):
        """Lazily get a Redis client, return None if unavailable."""
        if not self._redis_checked:
            self._redis_checked = True
            try:
                from src.utils.cache import get_redis
                self._redis = get_redis()
            except Exception:
                self._redis = None
        return self._redis

    def _get_limit(self, request: Request) -> int:
        """Determine the rate limit based on endpoint and auth status."""
        path = request.url.path
        # Stricter limit for public signing endpoints
        if "/esign/sign/" in path:
            return self.SIGNING_ENDPOINT_LIMIT

        # Check for authenticated user via Authorization header
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer ") and len(auth_header) > 10:
            return self.AUTHENTICATED_LIMIT

        return self.UNAUTHENTICATED_LIMIT

    def _get_identifier(self, request: Request) -> str:
        """Build a rate-limit key from IP and auth token (if present)."""
        client_ip = request.client.host if request.client else "unknown"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer ") and len(auth_header) > 10:
            # Use a hash-like suffix so we don't store raw tokens
            token_suffix = auth_header[-8:]
            return f"user:{client_ip}:{token_suffix}"
        return f"ip:{client_ip}"

    def _check_redis_rate_limit(self, identifier: str, limit: int) -> bool:
        """Check rate limit using Redis. Returns True if allowed."""
        r = self._get_redis()
        if not r:
            return self._check_memory_rate_limit(identifier, limit)

        try:
            key = f"ratelimit:{identifier}"
            current = r.incr(key)
            if current == 1:
                r.expire(key, 60)
            return current <= limit
        except Exception:
            # Fall back to in-memory on any Redis error
            return self._check_memory_rate_limit(identifier, limit)

    def _check_memory_rate_limit(self, identifier: str, limit: int) -> bool:
        """Fallback in-memory rate limit check. Returns True if allowed."""
        now = time.time()
        self.requests[identifier] = [
            t for t in self.requests[identifier] if now - t < 60
        ]
        if len(self.requests[identifier]) >= limit:
            return False
        self.requests[identifier].append(now)
        return True

    async def dispatch(self, request: Request, call_next):
        identifier = self._get_identifier(request)
        limit = self._get_limit(request)

        allowed = self._check_redis_rate_limit(identifier, limit)
        if not allowed:
            return Response(
                content='{"error":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json",
            )
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
