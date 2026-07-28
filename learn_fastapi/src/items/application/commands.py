from dataclasses import dataclass

from learn_fastapi.src.items.application.ports import ImageUpload
from learn_fastapi.src.items.domain.entities import Item
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId


@dataclass(frozen=True, slots=True)
class CreateItemCommand:
    item_data: Item
    owner_id: UserId


@dataclass(frozen=True, slots=True)
class UpdateItemCommand:
    item_id: ItemId
    owner_id: UserId | None
    is_superuser: bool
    fields: Item


@dataclass(frozen=True, slots=True)
class PatchItemCommand:
    item_id: ItemId
    owner_id: UserId | None
    is_superuser: bool
    fields: dict[str, object]


@dataclass(frozen=True, slots=True)
class DeleteItemCommand:
    item_id: ItemId
    owner_id: UserId
    is_superuser: bool


@dataclass(frozen=True, slots=True)
class CreateItemWithImageCommand:
    owner_id: UserId
    name: str
    price: float
    tax: float
    image_file: ImageUpload
    caption: str
    description: str = "No description provided"


@dataclass(frozen=True, slots=True)
class UpdateItemImageCommand:
    item_id: ItemId
    owner_id: UserId
    is_superuser: bool
    image_file: ImageUpload
    caption: str | None
