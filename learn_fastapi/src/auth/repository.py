from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.models import User

from .models import RefreshToken


class AuthRepository:
    """Repository class for auth-related ORM operations."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the repository with an async database session."""
        self.session: AsyncSession = session

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by primary key.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password_hash: str) -> User:
        """Persist a new user.

        Args:
            email: The user's email address.
            password_hash: The Argon2 password hash to store.

        Returns:
            The newly created and refreshed user instance.

        """
        user = User(email=email, password_hash=password_hash)
        self.session.add(user)
        await self.commit()
        await self.session.refresh(user)
        return user

    async def get_refresh_token(self, user_id: UUID) -> RefreshToken | None:
        """Fetch a refresh token.

        Args:
            user_id: The UUID of the user whose refresh token to retrieve.

        Returns:
            The matching refresh token or ``None`` if no valid token exists.

        """
        refresh_token = RefreshToken.__table__.c
        statement = (
            select(RefreshToken)
            .where(refresh_token.user_id == user_id)
            .where(refresh_token.revoked_at.is_(None))
            .where(refresh_token.expires_at > datetime.now(tz=UTC))
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create_refresh_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a new refresh token.

        Args:
            user_id: Owner of the refresh token.
            token_hash: Hashed refresh token value.
            expires_at: Expiration timestamp.

        Returns:
            The newly created refresh token record.

        """
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(refresh_token)
        await self.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def revoke_refresh_token(self, user_id: UUID) -> None:
        """Revoke a refresh token record.

        Args:
            user_id: Owner of the refresh token.

        """
        refresh_tokens = RefreshToken.__table__.c
        await self.session.execute(
            update(RefreshToken)
            .where(refresh_tokens.user_id == user_id)
            .where(refresh_tokens.revoked_at.is_(None))
            .values(revoked_at=datetime.now(tz=UTC))
        )
        await self.commit()
