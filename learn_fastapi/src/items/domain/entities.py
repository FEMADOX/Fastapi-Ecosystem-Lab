from dataclasses import dataclass
from datetime import datetime

from learn_fastapi.src.items.domain.value_objects import (
    ImagePublicId,
    ImageUrl,
    ItemId,
    OwnerId,
)


@dataclass(slots=True)
class Item:
    """Domain entity representing an item."""

    id: ItemId | None
    owner_id: OwnerId
    name: str
    description: str
    price: float
    tax: float
    image_url: ImageUrl | None = None
    image_public_id: ImagePublicId | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_owned_by(self, user_id: OwnerId) -> bool:
        return self.owner_id == user_id

    @property
    def total_price(self) -> float:
        return self.price + self.tax

    @property
    def has_image(self) -> bool:
        return self.image_url is not None and self.image_public_id is not None


@dataclass(slots=True)
class ItemImage:
    """Domain entity representing an image associated with an item."""

    url: ImageUrl
    public_id: ImagePublicId
