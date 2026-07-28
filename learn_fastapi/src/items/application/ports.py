from typing import BinaryIO, Protocol

from learn_fastapi.src.items.domain.entities import (
    ItemImage,
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.domain.value_objects import ImagePublicId
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId

type PublishableItem = PersistedItem | PersistedItemWithImage


class ItemsCache(Protocol):
    """Protocol for item cache operations."""

    async def get_item(self, item_id: ItemId) -> PersistedItem | None: ...
    async def set_item(self, item: PersistedItem) -> None: ...

    async def list_items(self) -> list[PersistedItem] | None: ...
    async def set_items(self, items: list[PersistedItem]) -> None: ...

    async def get_owner_item(
        self, item_id: ItemId, owner_id: UserId
    ) -> PersistedItem | None: ...
    async def set_owner_item(self, item: PersistedItem) -> None: ...

    async def list_owner_items(
        self, owner_id: UserId
    ) -> list[PersistedItem] | None: ...
    async def set_owner_items(
        self, owner_id: UserId, items: list[PersistedItem]
    ) -> None: ...

    async def invalidate_all(self) -> None: ...


class ItemsEventPublisher(Protocol):
    """Protocol for sse in the item operations."""

    async def item_created(self, item: PublishableItem) -> None: ...
    async def item_updated(self, item: PublishableItem) -> None: ...
    async def item_image_updated(self, item: PublishableItem) -> None: ...
    async def item_deleted(self, item: PublishableItem) -> None: ...


class ImageUpload(Protocol):
    """File-like input required to upload an item image."""

    filename: str | None
    content_type: str | None
    file: BinaryIO

    async def seek(self, offset: int) -> None: ...


class ImageStorage(Protocol):
    """Application port for external image storage."""

    async def upload(
        self, image_file: ImageUpload, caption: str | None
    ) -> ItemImage: ...
    async def delete(self, image_public_id: ImagePublicId) -> bool: ...
