from datetime import UTC, datetime

from sqlalchemy import select, update

from learn_fastapi.src.auth.domain.entities import (
    PersistedRefreshToken,
)
from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM
from learn_fastapi.src.auth.utils import verify_refresh_token
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.shared.infrastructure.repository import BaseSQLAlchemyRepository

from .mappers import persisted_refresh_token_from_orm


class SQLAlchemyAuthRepository(BaseSQLAlchemyRepository):
    """Repository for managing auth using SQLAlchemy."""

    async def get_refresh_token(self, owner_id: UserId) -> PersistedRefreshToken | None:
        """Get a refresh token by owner id.

        Args:
            owner_id (UserId): The ID of the refresh token to retrieve.

        Returns:
            RefreshTokenDomain | None:
                The corresponding refresh token, or None if not found.

        """
        refresh_tokens = RefreshTokenORM.__table__.c
        statement = (
            select(RefreshTokenORM)
            .where(refresh_tokens.user_id == owner_id)
            .where(refresh_tokens.revoked_at.is_(None))
            .where(refresh_tokens.expires_at > datetime.now(tz=UTC))
            .order_by(refresh_tokens.created_at.desc())
        )
        result = await self.session.scalars(statement)
        token = result.first()

        if not token:
            return None

        return persisted_refresh_token_from_orm(token)

    async def create_refresh_token(
        self,
        user_id: UserId,
        token_hash: str,
        expires_at: datetime,
    ) -> PersistedRefreshToken:
        """Persist a new refresh token.

        Args:
            user_id: Owner of the refresh token.
            token_hash: Hashed refresh token value.
            expires_at: Expiration timestamp.

        Returns:
            The newly created refresh token record.

        """
        refresh_token = RefreshTokenORM(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return persisted_refresh_token_from_orm(refresh_token)

    async def revoke_refresh_tokens(self, owner_id: UserId) -> None:
        """Revoke all active refresh tokens of a given user.

        Args:
            owner_id: The owner of the refresh token to revoke.

        """
        refresh_tokens = RefreshTokenORM.__table__.c
        await self.session.execute(
            update(RefreshTokenORM)
            .where(refresh_tokens.user_id == owner_id)
            .where(refresh_tokens.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self.session.commit()

    async def revoke_refresh_token(
        self, token: PersistedRefreshToken, token_raw: str
    ) -> None:
        """Revoke a refresh token from the specified user.

        Args:
            token: The refresh token to revoke.
            token_raw: The raw refresh token string to verify.

        """
        if not verify_refresh_token(token_raw, token.token_hash):
            return

        refresh_tokens = RefreshTokenORM.__table__.c
        await self.session.execute(
            update(RefreshTokenORM)
            .where(refresh_tokens.id == token.id)
            .where(refresh_tokens.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self.session.commit()
