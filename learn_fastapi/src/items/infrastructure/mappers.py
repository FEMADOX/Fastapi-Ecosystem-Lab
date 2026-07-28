from learn_fastapi.src.items.domain.entities import (
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.models import Item as ItemModel


def persisted_item_from_orm(orm_item: ItemModel) -> PersistedItem:
    """Convert an ORM item to a persisted item.

    Args:
        orm_item: The ORM item to convert.

    Returns:
        PersistedItem: The corresponding persisted item.

    """
    return PersistedItem(
        id=orm_item.id,
        owner_id=orm_item.user_id,
        name=orm_item.name,
        description=orm_item.description,
        price=orm_item.price,
        tax=orm_item.tax,
        image_url=orm_item.image_url,
        image_public_id=orm_item.image_public_id,
    )


def persisted_items_from_orm(orm_items: list[ItemModel]) -> list[PersistedItem]:
    """Convert a list of ORM items to a list of domain items.

    Args:
        orm_items: The list of ORM items to convert.

    Returns:
        list[PersistedItem]: The corresponding list of domain items.

    """
    return [persisted_item_from_orm(orm_item) for orm_item in orm_items]


def persisted_item_with_image_from_orm(
    orm_item: ItemModel,
) -> PersistedItemWithImage:
    """Convert an ORM item to a persisted item with image.

    Args:
        orm_item: The ORM item to convert.

    Returns:
        PersistedItem: The corresponding persisted item.

    """
    return PersistedItemWithImage(
        id=orm_item.id,
        owner_id=orm_item.user_id,
        name=orm_item.name,
        description=orm_item.description,
        price=orm_item.price,
        tax=orm_item.tax,
        image_url=orm_item.image_url,
        image_public_id=orm_item.image_public_id or "",
    )
