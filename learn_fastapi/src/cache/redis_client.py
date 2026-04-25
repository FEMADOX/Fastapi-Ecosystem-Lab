"""Async Redis client and low-level cache primitives.

Usage::
    from learn_fastapi.src.cache.redis_client import get_cache, set_cache, delete_cache

The module is intentionally fault-tolerant: every public coroutine catches
all Redis exceptions and logs a warning instead of propagating the error, so
a missing or unreachable Redis instance never breaks the API.
"""

import json
import logging
from typing import Any

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

_redis_client: aioredis.Redis | None = None


def get_redis_client() -> aioredis.Redis:
    """Return (or create) the shared async Redis client.

    ``from_url`` is synchronous — it builds the client object and configures
    the connection pool but does NOT open a socket.  The actual TCP connection
    is established on the first command.

    Returns:
        Configured ``redis.asyncio.Redis`` instance.

    """
    global _redis_client

    if not _redis_client:
        from learn_fastapi.src.config import settings

        _redis_client = aioredis.from_url(
            settings.redis_url, encoding="utf-8", decode_responses=False
        )

    return _redis_client


async def close_redis() -> None:
    """Close the Redis connection pool and reset the singleton.

    Called from the FastAPI ``lifespan`` context manager on shutdown.
    """
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None


async def get_cache(key: str) -> Any | None:
    """Fetch and deserialized a cached value.

    Args:
        key: Cache key.

    Returns:
        The deserialized Python object, or ``None`` on a cache miss or error.

    """
    try:
        client = get_redis_client()
        raw = await client.get(key)
        return json.loads(raw) if raw else None
    except Exception as exc:
        logger.warning(f"Failed to get cache for key '{key}': {exc}")
        return None


async def set_cache(key: str, value: Any, ttl: int = 300) -> None:
    """Serialize *value* to JSON and store it under *key* with a TTL.

    Args:
        key: Cache key.
        value: Any JSON-serializable object (UUIDs are coerced via ``default=str``).
        ttl: Expiry in seconds.  Defaults to 5 minutes.

    """
    try:
        client = get_redis_client()
        parsed_value = json.dumps(value, default=str)
        await client.setex(key, ttl, parsed_value)
    except Exception as exc:
        logger.warning(f"Failed to set cache for key '{key}': {exc}")


async def delete_cache(*keys: str) -> None:
    """Remove one or more cache entries.

    Args:
        *keys: One or more cache keys to delete.

    """
    if not keys:
        return
    try:
        client = get_redis_client()
        await client.delete(*keys)
    except Exception as exc:
        logger.warning(f"Failed to delete cache for keys {keys}: {exc}")


async def delete_cache_pattern(pattern: str) -> None:
    """Delete every key that matches *pattern* (e.g. ``"items:*"``).

    Uses ``KEYS`` — fine for development / low-traffic scenarios.
    For high-traffic production workloads prefer ``SCAN``-based iteration.

    Args:
        pattern: Redis glob pattern.

    """
    try:
        client = get_redis_client()
        matched = await client.keys(pattern)
        await client.delete(*matched) if matched else None
    except Exception as exc:
        logger.warning(f"Failed to delete cache for pattern {pattern}: {exc}")


def build_cache_key(namespace: str, *parts: str) -> str:
    """Construct a namespaced cache key.

    Args:
        namespace: Top-level bucket (e.g. ``"items"``).
        *parts: Additional segments joined with ``:``.

    Returns:
        A string such as ``"items:all"`` or ``"items:3fa85f64-..."``.

    """
    segments = ":".join(parts)
    return f"{namespace}:{segments}" if segments else namespace
