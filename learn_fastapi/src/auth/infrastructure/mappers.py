from learn_fastapi.src.auth.domain.entities import (
    PersistedRefreshToken,
)
from learn_fastapi.src.auth.domain.entities import (
    RefreshToken as RefreshTokenDomain,
)
from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM


def refresh_token_from_orm(orm_token: RefreshTokenORM) -> RefreshTokenDomain:
    """Convert an ORM refresh token to a domain refresh token.

    Args:
        orm_token (RefreshTokenORM): The ORM refresh token to convert.

    Returns:
        RefreshTokenDomain: The corresponding domain refresh token.

    """
    return RefreshTokenDomain(
        id=orm_token.id,
        owner_id=orm_token.user_id,
        token_hash=orm_token.token_hash,
        created_at=orm_token.created_at,
        expires_at=orm_token.expires_at,
        revoked_at=orm_token.revoked_at,
    )


def persisted_refresh_token_from_orm(
    orm_token: RefreshTokenORM,
) -> PersistedRefreshToken:
    """Convert an ORM refresh token to a persisted refresh token.

    Args:
        orm_token: The ORM refresh token to convert.

    Returns:
        PersistedRefreshToken: The corresponding persisted refresh token.

    """
    return PersistedRefreshToken(
        id=orm_token.id,
        owner_id=orm_token.user_id,
        token_hash=orm_token.token_hash,
    )
