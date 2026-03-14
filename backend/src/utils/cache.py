import json
import redis
from typing import Any, Callable, Optional
from functools import wraps
from src.config import get_settings

settings = get_settings()

_redis_client = None


def get_redis() -> Optional[redis.Redis]:
    """Get Redis client, return None if not available."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    r = get_redis()
    if not r:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """Set value in cache with TTL in seconds."""
    r = get_redis()
    if not r:
        return
    try:
        r.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_delete(key: str) -> None:
    """Delete a cache key."""
    r = get_redis()
    if not r:
        return
    try:
        r.delete(key)
    except Exception:
        pass


def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern."""
    r = get_redis()
    if not r:
        return
    try:
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
    except Exception:
        pass


def cached(key_prefix: str, ttl: int = 3600):
    """Decorator to cache function results."""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{':'.join(str(a) for a in args)}"
            result = cache_get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
