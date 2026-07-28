from learn_fastapi.src.items.domain.entities import (
    Item as ItemDomain,
)
from learn_fastapi.src.items.domain.entities import (
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.presentation.schemas import ItemSchema, ItemUpdateSchema
from learn_fastapi.src.shared.application.dto import AuthenticatedAccount, CurrentActor
from learn_fastapi.src.shared.domain.value_object import UserId


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


def persisted_items_to_schema(persisted_items: list[PersistedItem]) -> list[ItemSchema]:
    """Convert a list of domain items to a list of schema items.

    Args:
        persisted_items: The list of domain items to convert.

    Returns:
        list[ItemSchema]: The corresponding list of schema items.

    """
    return [persisted_item_to_schema(domain_item) for domain_item in persisted_items]


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


def current_actor_from_user(user: AuthenticatedAccount) -> CurrentActor:
    return CurrentActor(
        id=user.id,
        is_superuser=user.is_superuser,
    )


def item_from_update_schema(
    item_data: ItemUpdateSchema, owner_id: UserId | None
) -> ItemDomain:
    item_owner_id = item_data.user_id or owner_id
    if item_owner_id is None:
        msg = "owner_id is required to build an item domain entity"
        raise ValueError(msg)

    return ItemDomain(
        id=None,
        owner_id=item_owner_id,
        name=item_data.name,
        description=item_data.description or "No description provided",
        price=item_data.price,
        tax=item_data.tax,
        image_url=item_data.image_url or "",
    )
