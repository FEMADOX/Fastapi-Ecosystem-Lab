from dataclasses import dataclass
from datetime import datetime

from learn_fastapi.src.items.domain.value_objects import (
    ImagePublicId,
    ImageUrl,
)
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId


@dataclass(frozen=True, slots=True)
class Item:
    """Domain entity representing an item."""

    id: ItemId | None
    owner_id: UserId
    name: str
    description: str
    price: float
    tax: float
    image_url: ImageUrl = ""
    image_public_id: ImagePublicId | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_owned_by(self, user_id: UserId) -> bool:
        return self.owner_id == user_id

    @property
    def total_price(self) -> float:
        return self.price + self.tax

    @property
    def has_image(self) -> bool:
        return self.image_url is not None and self.image_public_id is not None


@dataclass(frozen=True, slots=True)
class PersistedItem:
    """Domain entity representing a persistent item."""

    id: ItemId
    owner_id: UserId
    name: str
    description: str
    price: float
    tax: float
    image_url: ImageUrl | None
    image_public_id: ImagePublicId | None


@dataclass(frozen=True, slots=True)
class ItemImage:
    """Domain entity representing a persisted image associated with an item."""

    name: str
    content_type: str | None
    url: ImageUrl
    public_id: ImagePublicId
    description: str | None = "No description provided"


@dataclass(frozen=True, slots=True)
class PersistedItemWithImage:
    """Domain entity representing a persistent item with an image."""

    id: ItemId
    owner_id: UserId
    name: str
    description: str
    price: float
    tax: float
    image_url: ImageUrl
    image_public_id: ImagePublicId
