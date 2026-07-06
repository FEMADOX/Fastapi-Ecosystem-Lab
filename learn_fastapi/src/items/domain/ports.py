from typing import Protocol

from learn_fastapi.src.items.domain.entities import Item
from learn_fastapi.src.items.domain.value_objects import ItemId, OwnerId


class ItemRepository(Protocol):
    """Protocol for item repository operations."""

    async def list_items(self) -> list[Item]: ...
    async def get_item_by_id(self, item_id: ItemId) -> Item | None: ...
    async def list_owner_items(self, owner_id: OwnerId) -> list[Item]: ...
    async def get_owner_item(
        self, item_id: ItemId, owner_id: OwnerId
    ) -> Item | None: ...
