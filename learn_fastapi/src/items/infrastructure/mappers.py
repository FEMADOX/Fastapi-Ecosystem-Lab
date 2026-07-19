from learn_fastapi.src.items.domain.entities import (
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.models import Item as ItemModel
from learn_fastapi.src.items.schema import ItemSchema


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


def persisted_item_to_schema(persisted_item: PersistedItem) -> ItemSchema:
    """Convert a domain item to a schema item.

    Args:
        persisted_item: The domain item to convert.

    Returns:
        ItemSchema: The corresponding schema item.

    """
    return ItemSchema(
        id=persisted_item.id,
        user_id=persisted_item.owner_id,
        name=persisted_item.name,
        description=persisted_item.description,
        price=persisted_item.price,
        tax=persisted_item.tax,
        image_url=persisted_item.image_url,
    )


def persisted_items_from_orm(orm_items: list[ItemModel]) -> list[PersistedItem]:
    """Convert a list of ORM items to a list of domain items.

    Args:
        orm_items: The list of ORM items to convert.

    Returns:
        list[PersistedItem]: The corresponding list of domain items.

    """
    return [persisted_item_from_orm(orm_item) for orm_item in orm_items]


def persisted_items_to_schema(persisted_items: list[PersistedItem]) -> list[ItemSchema]:
    """Convert a list of domain items to a list of schema items.

    Args:
        persisted_items: The list of domain items to convert.

    Returns:
        list[ItemSchema]: The corresponding list of schema items.

    """
    return [persisted_item_to_schema(domain_item) for domain_item in persisted_items]


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


def persisted_item_with_image_to_schema(
    persisted_item_with_image: PersistedItemWithImage,
) -> ItemSchema:
    """Convert a persisted item with image to a schema item.

    Args:
        persisted_item_with_image: The domain item to convert.

    Returns:
        ItemSchema: The corresponding schema item.

    """
    return ItemSchema(
        id=persisted_item_with_image.id,
        user_id=persisted_item_with_image.owner_id,
        name=persisted_item_with_image.name,
        description=persisted_item_with_image.description,
        price=persisted_item_with_image.price,
        tax=persisted_item_with_image.tax,
        image_url=persisted_item_with_image.image_url,
    )
