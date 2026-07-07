from uuid import UUID

from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.models import User as UserORM
from learn_fastapi.src.users.schema import UserResponse


def user_from_orm(orm_user: UserORM) -> UserDomain:
    """Convert an ORM item to a domain item.

    Args:
        orm_user (ItemORM): The ORM item to convert.

    Returns:
        ItemDomain: The corresponding domain item.

    """
    items_ids = [item.id for item in orm_user.items]
    refresh_tokens_ids = [refresh_token.id for refresh_token in orm_user.refresh_tokens]
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


def user_domain_to_schema(domain_user: UserDomain) -> UserResponse:
    """Convert an Domain user to a schema user.

    Args:
        domain_user (UserDomain): The domain user to convert.

    Returns:
        UserResponse: The corresponding schema user.

    """
    return UserResponse(
        id=domain_user.id or UUID(),
        email=domain_user.email,
        is_active=domain_user.is_active,
        is_superuser=domain_user.is_superuser,
    )
