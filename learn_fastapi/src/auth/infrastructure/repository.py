from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from learn_fastapi.src.auth.domain.entities import RefreshToken as RefreshTokenDomain
from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM
from learn_fastapi.src.auth.utils import verify_refresh_token
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.infrastructure.mappers import user_from_orm
from learn_fastapi.src.users.models import User as UserORM
from learn_fastapi.src.utils.repository import bool_to_column

from .mappers import refresh_token_from_orm


class SQLAlchemyAuthRepository:
    """Repository for managing auth using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous SQLAlchemy session."""
        self.session = session

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
        tokens = result.all()
        if not tokens:
            return None

        # If there are multiple tokens, keep only the newest and revoke the rest
        if len(tokens) > 1:
            newest_token = tokens[0]

            # TODO (FENYXZ): This shouldn't be in a read action
            # Revoke all tokens except the newest
            # for old_token in tokens[1:]:
            #     old_token.revoked_at = datetime.now(tz=UTC)
            #     self.session.add(old_token)
            # await self.session.commit()

            return refresh_token_from_orm(newest_token)

        return refresh_token_from_orm(tokens[0])

    async def get_user_from_refresh_token(
        self, refresh_token: str
    ) -> UserDomain | None:
        """Get the user associated with a valid refresh token.

        Args:
            refresh_token: The raw refresh token string to validate and search for.

        Returns:
            The associated user if the token is valid, or None if invalid.

        """
        # Argon2 hashes are salted, so hashing again and comparing with SQL equality
        # cannot match the stored value; fetch active tokens and verify per row.
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
