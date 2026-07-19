from typing import Protocol

from learn_fastapi.src.items.domain.entities import (
    ImageUploadFile,
    ItemImage,
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.domain.entities import Item as ItemDomain
from learn_fastapi.src.items.domain.value_objects import ImagePublicId
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId


class ItemsRepository(Protocol):
    """Protocol for item repository operations."""

    async def list_items(self) -> list[PersistedItem]: ...
    async def get_item_by_id(self, item_id: ItemId) -> PersistedItem | None: ...
    async def get_item_by_name(self, item_name: str) -> PersistedItem | None: ...
    async def list_owner_items(self, owner_id: UserId) -> list[PersistedItem]: ...
    async def get_owner_item(
        self, item_id: ItemId, owner_id: UserId
    ) -> PersistedItem | None: ...
    async def create_item(
        self, owner_id: UserId, item_data: ItemDomain
    ) -> PersistedItem: ...
    async def update_item(
        self,
        item_id: ItemId,
        item_data: ItemDomain,
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> PersistedItem | None: ...
    async def patch_item(
        self,
        item_id: ItemId,
        item_data: dict[str, object],
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> PersistedItem | None: ...
    async def delete_item(
        self, item_id: ItemId, owner_id: UserId | None = None
    ) -> PersistedItem | None: ...
    async def create_item_with_image(  # noqa: PLR0913, PLR0917
        self,
        owner_id: UserId,
        name: str,
        description: str,
        price: float,
        tax: float,
        image: ItemImage,
    ) -> PersistedItemWithImage: ...
    async def update_item_with_image(
        self,
        item_id: ItemId,
        owner_id: UserId | None,
        image: ItemImage,
    ) -> PersistedItemWithImage | None: ...


class ImageStorage(Protocol):
    """Protocol for image storage operations."""

    async def upload(
        self, image_file: ImageUploadFile, caption: str | None
    ) -> ItemImage: ...
    async def delete(self, image_public_id: ImagePublicId) -> bool: ...
