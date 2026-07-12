from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from learn_fastapi.src.auth.domain.entities import RefreshToken as RefreshTokenDomain
from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM
from learn_fastapi.src.auth.utils import verify_refresh_token
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.shared.infrastructure.repository import BaseSQLAlchemyRepository
from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.infrastructure.mappers import user_from_orm
from learn_fastapi.src.users.models import User as UserORM
from learn_fastapi.src.utils.repository import bool_to_column

from .mappers import refresh_token_from_orm


class SQLAlchemyAuthRepository(BaseSQLAlchemyRepository):
    """Repository for managing auth using SQLAlchemy."""

    async def get_refresh_token(self, owner_id: UserId) -> RefreshTokenDomain | None:
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

        return refresh_token_from_orm(token)

    async def get_user_from_refresh_token(
        self, refresh_token: str
    ) -> UserDomain | None:
        """Get the user associated with a valid refresh token.

        Args:
            refresh_token: The raw refresh token string to validate and search for.

        Returns:
            The associated user if the token is valid, or None if invalid.

        """
        statement = (
            select(RefreshTokenORM)
            .join(RefreshTokenORM.user)
            .where(RefreshTokenORM.__table__.c.revoked_at.is_(None))
            .where(bool_to_column(RefreshTokenORM.expires_at > datetime.now(tz=UTC)))
            .options(
                selectinload(RefreshTokenORM.user).selectinload(UserORM.items),
                selectinload(RefreshTokenORM.user).selectinload(UserORM.refresh_tokens),
            )
        )
        result = await self.session.scalars(statement)
        for token_record in result.all():
            if verify_refresh_token(refresh_token, token_record.token_hash):
                return user_from_orm(token_record.user)

        return None

    async def create_refresh_token(
        self,
        user_id: UserId,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshTokenDomain:
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
        return refresh_token_from_orm(refresh_token)

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
        self, token: RefreshTokenDomain, token_raw: str
    ) -> None:
        """Revoke a refresh token from the specified user.

        Args:
            token: The refresh token to revoke.
            token_raw: The raw refresh token string to verify.

        """
        if not token.id or not verify_refresh_token(token_raw, token.token_hash):
            return

        refresh_tokens = RefreshTokenORM.__table__.c
        await self.session.execute(
            update(RefreshTokenORM)
            .where(refresh_tokens.id == token.id)
            .where(refresh_tokens.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self.session.commit()
