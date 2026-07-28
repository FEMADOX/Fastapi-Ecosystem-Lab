from pydantic import BaseModel, TypeAdapter, ValidationError

from learn_fastapi.src.cache.redis_client import (
    build_cache_key,
    delete_cache,
    delete_cache_pattern,
    get_cache,
    set_cache,
)
from learn_fastapi.src.items.domain.entities import PersistedItem
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId

_NS = "items"
_TTL = 600

_ALL_KEY = build_cache_key(_NS, "all")


class ItemCacheRecord(BaseModel):
    """Formato interno con el que un item se guarda en Redis."""

    id: ItemId
    owner_id: UserId
    name: str
    description: str
    price: float
    tax: float
    image_url: str | None
    image_public_id: str | None

    @classmethod
    def from_domain(cls, item: PersistedItem) -> ItemCacheRecord:
        return cls(
            id=item.id,
            owner_id=item.owner_id,
            name=item.name,
            description=item.description,
            price=item.price,
            tax=item.tax,
            image_url=item.image_url,
            image_public_id=item.image_public_id,
        )

    def to_domain(self) -> PersistedItem:
        return PersistedItem(
            id=self.id,
            owner_id=self.owner_id,
            name=self.name,
            description=self.description,
            price=self.price,
            tax=self.tax,
            image_url=self.image_url,
            image_public_id=self.image_public_id,
        )


_item_records_adapter = TypeAdapter(list[ItemCacheRecord])


def _item_key(item_id: ItemId) -> str:
    """Return the cache key for a single item.

    Returns:
        A string like ``"items:123e4567-e89b-12d3-a456-426614174000"``.

    """
    return build_cache_key(_NS, "by-id", str(item_id))


def _owner_item_key(item_id: ItemId, owner_id: UserId) -> str:
    """Return the cache key for a single user's item.

    Returns:
        A string like ``"items:3fa85f64-5717-4562-b3fc-2c963f66afa6:123e4567..."``
            for a single item, or ``"items:3fa85f64-..."`` for the full list.

    """
    # if item_id:
    #     return build_cache_key(_NS, f"{item_id}:{owner.id}")
    return build_cache_key(_NS, "owner", str(owner_id), "item", str(item_id))


def _owner_items_key(owner_id: UserId) -> str:
    return build_cache_key(_NS, "owner", str(owner_id))


class RedisItemCache:
    """Redis adapter that implements the item cache port."""

    async def get_item(self, item_id: ItemId) -> PersistedItem | None:
        """Retrieve one item from Redis.

        Args:
            item_id: The ID of the item to retrieve.

        Returns:
            The cached item, or ``None`` when the key is missing or its payload
            cannot be validated.

        """
        payload = await get_cache(_item_key(item_id))
        if not isinstance(payload, dict):
            return None

        try:
            return ItemCacheRecord.model_validate(payload).to_domain()
        except ValidationError:
            return None

    async def set_item(self, item: PersistedItem) -> None:
        """Store one item in Redis using the configured cache TTL.

        Args:
            item: The persisted item to cache.

        """
        record = ItemCacheRecord.from_domain(item)
        await set_cache(
            _item_key(item.id),
            record.model_dump_json(),
            ttl=_TTL,
        )

    async def list_items(self) -> list[PersistedItem] | None:
        """Retrieve the cached list of all items.

        Returns:
            The cached items, or ``None`` when the key is missing or its
            payload cannot be validated.

        """
        payload = await get_cache(_ALL_KEY)
        if not isinstance(payload, list):
            return None

        try:
            records = _item_records_adapter.validate_python(payload)
        except ValidationError:
            return None

        return [record.to_domain() for record in records]

    async def set_items(self, items: list[PersistedItem]) -> None:
        """Store the full item list in Redis using the configured TTL.

        Args:
            items: The persisted items to cache.

        """
        records = [ItemCacheRecord.from_domain(item) for item in items]
        payload = [record.model_dump_json() for record in records]

        await set_cache(_ALL_KEY, payload, ttl=_TTL)

    async def get_owner_item(
        self, item_id: ItemId, owner_id: UserId
    ) -> PersistedItem | None:
        """Retrieve one cached item scoped to its owner.

        Args:
            item_id: The ID of the item to retrieve.
            owner_id: The ID of the owner whose item is requested.

        Returns:
            The cached item when it belongs to ``owner_id``; otherwise ``None``.

        """
        payload = await get_cache(_owner_item_key(item_id, owner_id))
        if not isinstance(payload, dict):
            return None

        try:
            item = ItemCacheRecord.model_validate(payload).to_domain()
        except ValidationError:
            return None

        return item if item.owner_id == owner_id else None

    async def set_owner_item(self, item: PersistedItem) -> None:
        """Store one item under its owner-scoped cache key.

        Args:
            item: The persisted item to cache.

        """
        record = ItemCacheRecord.from_domain(item)

        await set_cache(
            _owner_item_key(item.id, item.owner_id), record.model_dump_json(), _TTL
        )

    async def list_owner_items(self, owner_id: UserId) -> list[PersistedItem] | None:
        """Retrieve the cached items belonging to one owner.

        Args:
            owner_id: The ID of the owner whose items are requested.

        Returns:
            The owner's cached items, or ``None`` when the key is missing or
            its payload is invalid.

        """
        payload = await get_cache(_owner_items_key(owner_id))
        if not isinstance(payload, list):
            return None

        try:
            records = _item_records_adapter.validate_python(payload)
        except ValidationError:
            return None

        items = [record.to_domain() for record in records]

        return items if all(item.owner_id == owner_id for item in items) else None

    async def set_owner_items(
        self,
        owner_id: UserId,
        items: list[PersistedItem],
    ) -> None:
        """Store the owner's item list in Redis.

        Args:
            owner_id: The ID of the owner associated with the cached list.
            items: The persisted items to cache.

        Raises:
            ValueError: If an item does not belong to ``owner_id``.

        """
        if any(item.owner_id != owner_id for item in items):
            msg = "All cached items must belong to the requested owner"
            raise ValueError(msg)

        records = [ItemCacheRecord.from_domain(item) for item in items]
        payload = [record.model_dump_json() for record in records]

        await set_cache(_owner_items_key(owner_id), payload, _TTL)

    async def invalidate_all(self) -> None:
        """Invalidate every item-related key in Redis.

        This removes individual item keys, global lists, and owner-scoped
        entries so writes cannot leave stale item data behind.

        """
        await delete_cache_pattern("items:*")

    async def invalidate_cache(self, item_id: ItemId) -> None:
        """Invalidate one globally cached item.

        Args:
            item_id: The ID of the item whose global cache entry is removed.

        Note:
            This does not remove owner-scoped entries for the same item. Use
            ``invalidate_all`` when a mutation must clear every representation.

        """
        await delete_cache(_item_key(item_id))
