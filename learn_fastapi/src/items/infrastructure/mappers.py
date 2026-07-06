from learn_fastapi.src.items.application.dto import ItemDTO
from learn_fastapi.src.items.domain.entities import Item as ItemDomain
from learn_fastapi.src.items.models import Item as ItemORM
from learn_fastapi.src.items.schema import ItemSchema


def item_from_orm(orm_item: ItemORM) -> ItemDomain:
    """Convert an ORM item to a domain item.

    Args:
        orm_item (ItemORM): The ORM item to convert.

    Returns:
        ItemDomain: The corresponding domain item.

    """
    return ItemDomain(
        id=orm_item.id,
        owner_id=orm_item.user_id,
        name=orm_item.name,
        description=orm_item.description,
        price=orm_item.price,
        tax=orm_item.tax,
        image_url=orm_item.image_url,
        image_public_id=orm_item.image_public_id,
        created_at=orm_item.created_at,
        updated_at=orm_item.updated_at,
    )


def item_domain_to_schema(domain_item: ItemDomain) -> ItemSchema:
    """Convert a domain item to a schema item.

    Args:
        domain_item (ItemDomain): The domain item to convert.

    Returns:
        ItemSchema: The corresponding schema item.

    """
    return ItemSchema(
        id=domain_item.id,
        user_id=domain_item.owner_id,
        name=domain_item.name,
        description=domain_item.description,
        price=domain_item.price,
        tax=domain_item.tax,
        image_url=domain_item.image_url,
    )


def items_from_orm(orm_items: list[ItemORM]) -> list[ItemDomain]:
    """Convert a list of ORM items to a list of domain items.

    Args:
        orm_items (list[ItemORM]): The list of ORM items to convert.

    Returns:
        list[ItemDomain]: The corresponding list of domain items.

    """
    return [item_from_orm(orm_item) for orm_item in orm_items]


def items_domain_to_schema(domain_items: list[ItemDomain]) -> list[ItemSchema]:
    """Convert a list of domain items to a list of schema items.

    Args:
        domain_items (list[ItemDomain]): The list of domain items to convert.

    Returns:
        list[ItemSchema]: The corresponding list of schema items.

    """
    return [item_domain_to_schema(domain_item) for domain_item in domain_items]


def item_to_dto(domain_item: ItemDomain) -> ItemDTO:
    return ItemDTO(
        id=domain_item.id,
        owner_id=domain_item.owner_id,
        name=domain_item.name,
        description=domain_item.description,
        price=domain_item.price,
        tax=domain_item.tax,
        image_url=domain_item.image_url,
    )
