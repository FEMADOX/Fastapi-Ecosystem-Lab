from learn_fastapi.src.auth.models import RefreshToken
from learn_fastapi.src.items.models import Item
from learn_fastapi.src.shared.domain.value_object import ItemId, RefreshTokenId
from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.models import User as UserModel
from learn_fastapi.src.users.schema import UserResponse


def obtain_items_and_refresh_tokens_ids(
    items: list[Item],
    refresh_tokens: list[RefreshToken],
) -> tuple[list[ItemId], list[RefreshTokenId]]:
    """Obtain the items and refresh tokens ids.

    Args:
        items: A list of items.
        refresh_tokens: A list of refresh token.

    Returns:
        list[ItemId]: The items ids.
        list[RefreshTokenId]: The refresh token ids.

    """
    items_ids = [item.id for item in items if item.id is not None]
    refresh_tokens_ids = [
        refresh_token.id
        for refresh_token in refresh_tokens
        if refresh_token.id is not None
    ]
    return items_ids, refresh_tokens_ids


def domain_user_from_orm(
    orm_user: UserModel, include_relationships: bool = True
) -> UserDomain:
    """Convert an ORM item to a domain item.

    Args:
        orm_user: The ORM item to convert.
        include_relationships: Whether to include relationships.

    Returns:
        ItemDomain: The corresponding domain item.

    """
    items_ids, refresh_tokens_ids = (
        obtain_items_and_refresh_tokens_ids(orm_user.items, orm_user.refresh_tokens)
        if include_relationships
        else ([], [])
    )
    return UserDomain(
        id=orm_user.id,
        items_ids=items_ids,
        refresh_tokens_ids=refresh_tokens_ids,
        email=orm_user.email,
        password_hash=orm_user.password_hash,
        is_active=orm_user.is_active,
        is_superuser=orm_user.is_superuser,
        created_at=orm_user.created_at,
        updated_at=orm_user.updated_at,
    )


def persisted_user_from_orm(
    orm_user: UserModel, include_relationships: bool = True
) -> PersistedUser:
    """Convert an ORM user to a persisted user.

    Args:
        orm_user: The ORM user to convert.

    Returns:
        PersistedUser: The corresponding persisted user.

    """
    items_ids, refresh_tokens_ids = (
        obtain_items_and_refresh_tokens_ids(orm_user.items, orm_user.refresh_tokens)
        if include_relationships
        else ([], [])
    )
    return PersistedUser(
        orm_user.id,
        items_ids,
        refresh_tokens_ids,
        orm_user.email,
        orm_user.password_hash,
        orm_user.is_active,
        orm_user.is_superuser,
    )


def persisted_user_to_schema(persisted_user: PersistedUser) -> UserResponse:
    """Convert a Domain user to a schema user.

    Args:
        persisted_user: The domain user to convert.

    Returns:
        UserResponse: The corresponding schema user.

    """
    return UserResponse(
        id=persisted_user.id,
        email=persisted_user.email,
        is_active=persisted_user.is_active,
        is_superuser=persisted_user.is_superuser,
    )
