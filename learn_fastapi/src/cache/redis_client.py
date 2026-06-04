"""Async Redis client and low-level cache primitives.

Usage::
    from learn_fastapi.src.cache.redis_client import get_cache, set_cache, delete_cache

The module is intentionally fault-tolerant: every public coroutine catches
all Redis exceptions and logs a warning instead of propagating the error, so
a missing or unreachable Redis instance never breaks the API.
"""

import json
from collections.abc import Awaitable
from dataclasses import dataclass
from functools import lru_cache
from typing import cast

from redis import RedisError
from redis import asyncio as aioredis

from learn_fastapi.src.utils.alembic import app_logger

logger = app_logger

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | list[JSONValue] | dict[str, JSONValue]


@dataclass
class RedisCacheState:
    """Singleton state for Redis cache availability."""

    is_available: bool = True

    def disable(self) -> None:
        """Mark the Redis cache as unavailable."""
        self.is_available = False
        get_redis_client.cache_clear()

    def enable(self) -> None:
        """Mark the Redis cache as available."""
        self.is_available = True
        get_redis_client.cache_clear()


redis_cache_state = RedisCacheState()


@lru_cache(1)
def get_redis_client() -> aioredis.Redis | None:
    """Return (or create) the shared async Redis client.

    ``from_url`` is synchronous — it builds the client object and configures
    the connection pool but does NOT open a socket.  The actual TCP connection
    is established on the first command.

    Returns:
        Configured ``redis.asyncio.Redis`` instance.

    """
    from learn_fastapi.src.config import settings  # noqa: PLC0415

    if not redis_cache_state.is_available:
        return None

    return aioredis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=False
    )


async def close_redis() -> None:
    """Close the Redis connection pool and reset the singleton.

    Called from the FastAPI ``lifespan`` context manager on shutdown.
    """
    if get_redis_client.cache_info().currsize:
        client = get_redis_client()
        get_redis_client.cache_clear()
        if not client:
            return
        await client.aclose()


async def get_cache(key: str) -> JSONValue | None:
    """Fetch and deserialized a cached value.

    Args:
        key: Cache key.

    Returns:
        The deserialized Python object, or ``None`` on a cache miss or error.

    """
    try:
        client = get_redis_client()
        if not client:
            return None
        raw = await client.get(key)
        return json.loads(raw) if raw else None
    except json.JSONDecodeError, RedisError:
        logger.exception(f"Failed to get cache for key '{key}'")
        redis_cache_state.disable()
        return None


async def set_cache(key: str, value: JSONValue, ttl: int = 300) -> None:
    """Serialize *value* to JSON and store it under *key* with a TTL.

    Args:
        key: Cache key.
        value: JSON-serializable object.
        ttl: Expiry in seconds.  Defaults to 5 minutes.

    """
    try:
        client = get_redis_client()
        parsed_value = json.dumps(value, default=str)
        if not client:
            return
        await client.setex(key, ttl, parsed_value)
    except TypeError, ValueError, RedisError:
        logger.exception(f"Failed to set cache for key '{key}'")
        redis_cache_state.disable()


async def delete_cache(*keys: str) -> None:
    """Remove one or more cache entries.

    Args:
        *keys: One or more cache keys to delete.

    """
    if not keys:
        return
    try:
        client = get_redis_client()
        if not client:
            return
        await client.delete(*keys)
    except RedisError:
        logger.exception(f"Failed to delete cache for keys {keys}")
        redis_cache_state.disable()


async def delete_cache_pattern(pattern: str) -> None:
    """Delete every key that matches *pattern* (e.g. ``"items:*"``).

    Uses ``KEYS`` — fine for development / low-traffic scenarios.
    For high-traffic production workloads prefer ``SCAN``-based iteration.

    Args:
        pattern: Redis glob pattern.

    """
    try:
        client = get_redis_client()
        if not client:
            return
        matched = await client.keys(pattern)
        await client.delete(*matched) if matched else None
    except RedisError:
        logger.exception(f"Failed to delete cache for pattern {pattern}")
        redis_cache_state.disable()


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


async def check_redis_health() -> dict[str, str]:
    try:
        logger.info("[Redis]: Checking redis health...")
        client = cast("aioredis.Redis", get_redis_client())

        async def await_ping(value: Awaitable[bool] | bool) -> bool:
            if isinstance(value, bool):
                return value
            return await value

        pong = await await_ping(client.ping())
        if not pong:
            logger.warning("[Redis]: Connection failed")
            redis_cache_state.disable()
            return {"redis": "unhealthy"}
        logger.info("[Redis]: Status healthy")
        return {"redis": "healthy"}
    except Exception:
        logger.exception("[Redis]: Health check failed")
        redis_cache_state.disable()
        return {"redis": "unhealthy"}
