"""Cache helpers scoped to the items domain.

Key layout::

    items:all            → serialized list[ItemSchema]
    items:<uuid>         → serialized ItemSchema

TTL is 10 minutes for both key types.
"""

from typing import cast
from uuid import UUID

from learn_fastapi.src.cache.redis_client import (
    JSONValue,
    build_cache_key,
    delete_cache,
    delete_cache_pattern,
    get_cache,
    set_cache,
)
from learn_fastapi.src.users.models import User

from .schema import ItemSchema

_NS = "items"
_TTL = 600

type ItemCachePayload = dict[str, JSONValue]
type ItemCacheListPayload = list[ItemCachePayload]

_ALL_KEY = build_cache_key(_NS, "all")


def _item_key(item_id: UUID) -> str:
    """Return the cache key for a single item.

    Returns:
        A string like ``"items:123e4567-e89b-12d3-a456-426614174000"``.

    """
    return build_cache_key(_NS, str(item_id))


def _item_to_json(item: ItemSchema | ItemCachePayload) -> JSONValue:
    """Convert an ItemSchema or a pre-serialized dict to a JSONValue.

    ``service.py`` passes already-serialized dicts (via ``model_dump(mode="json")``),
    so we accept both forms to avoid a double-serialization / AttributeError.

    Returns:
        Item data as JSON data

    """
    if isinstance(item, dict):
        return item
    return item.model_dump(mode="json")


def _user_items_key(owner: User, item_id: UUID | None = None) -> str:
    """Return the cache key for a single user's item.

    Returns:
        A string like ``"items:3fa85f64-5717-4562-b3fc-2c963f66afa6:123e4567..."``
            for a single item, or ``"items:3fa85f64-..."`` for the full list.

    """
    if item_id:
        return build_cache_key(_NS, f"{item_id}:{owner.id}")
    return build_cache_key(_NS, f"{owner.id}")


# -------------------------------------------------------------------------------------
# Read Helpers
# -------------------------------------------------------------------------------------


async def get_cached_items() -> ItemCacheListPayload | None:
    """Return the cached full item list, or ``None`` on a miss.

    Returns:
        A list of item dicts, or ``None`` if the cache is empty or an error occurs.

    """
    return cast("ItemCacheListPayload | None", await get_cache(_ALL_KEY))


async def get_cached_item(item_id: UUID) -> ItemCachePayload | None:
    """Return a single cached item dict, or ``None`` on a miss.

    Returns:
        A dict representing the item, or ``None``
            if the cache is empty or an error occurs.

    """
    return cast("ItemCachePayload | None", await get_cache(_item_key(item_id)))


async def get_cached_user_item(item_id: UUID, owner: User) -> ItemCachePayload | None:
    """Return a single cached user's item dict, or ``None`` on a miss.

    Returns:
        A dict representing the user's item, or ``None``
            if the cache is empty or an error occurs.

    """
    return cast(
        "ItemCachePayload | None", await get_cache(_user_items_key(owner, item_id))
    )


async def get_cached_user_items(owner: User) -> ItemCacheListPayload | None:
    """Return the cached user's item list, or ``None`` on a miss.

    Returns:
        A list of user's item dicts, or ``None``
            if the cache is empty or an error occurs.

    """
    return cast("ItemCacheListPayload | None", await get_cache(_user_items_key(owner)))


# -------------------------------------------------------------------------------------
# Write Helpers
# -------------------------------------------------------------------------------------


async def cache_items(items_data: list[ItemSchema]) -> None:
    """Store the full item list in Redis."""
    payload = [_item_to_json(item) for item in items_data]
    await set_cache(_ALL_KEY, payload, ttl=_TTL)


async def cache_item(item_id: UUID, item_data: ItemSchema) -> None:
    """Store a single item list in Redis."""
    await set_cache(_item_key(item_id), _item_to_json(item_data), ttl=_TTL)


async def cache_user_items(items_data: list[ItemSchema], owner: User) -> None:
    """Store the user's item list in Redis."""
    payload = [_item_to_json(item) for item in items_data]
    await set_cache(_user_items_key(owner), payload, ttl=_TTL)


async def cache_user_item(item_id: UUID, item_data: ItemSchema, owner: User) -> None:
    """Store a single user's item in Redis."""
    await set_cache(_user_items_key(owner, item_id), _item_to_json(item_data), ttl=_TTL)


# -------------------------------------------------------------------------------------
# Delete Helpers
# -------------------------------------------------------------------------------------


async def invalidate_cache(item_id: UUID) -> None:
    """Invalidate a **single** cached item."""
    await delete_cache(_item_key(item_id))


async def invalidate_all_items() -> None:
    """Invalidate **all** cached items."""
    await delete_cache(_ALL_KEY)


async def invalidate_items_namespace() -> None:
    """Invalidate **all** items-related keys (single + list)."""
    await delete_cache_pattern(f"{_NS}:*")
