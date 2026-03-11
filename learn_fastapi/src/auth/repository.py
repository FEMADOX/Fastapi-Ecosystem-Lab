from datetime import datetime
from uuid import UUID

from sqlalchemy import select

from learn_fastapi.src.database import AsyncSessionDep

from .models import RefreshToken, User


class AuthRepository:
    """Repository class for auth-related ORM operations."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the repository with an async database session."""
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(select(User).where(User.email == email))  # ty: ignore[invalid-argument-type]
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by primary key.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(select(User).where(User.id == user_id))  # ty: ignore[invalid-argument-type]
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
        await self.session.commit()
        await self.session.refresh(user)
        return user

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
        await self.session.commit()
        await self.session.refresh(refresh_token)
        return refresh_token

    async def get_valid_refresh_tokens(self, now: datetime) -> list[RefreshToken]:
        """Fetch all unrevoked and unexpired refresh tokens.

        Args:
            now: Reference datetime for expiration comparison.

        Returns:
            A list of valid refresh token records.

        """
        result = await self.session.execute(
            select(RefreshToken)  # ty: ignore[invalid-argument-type]
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > now)
        )
        return list(result.scalars().all())

    async def get_active_refresh_tokens(self) -> list[RefreshToken]:
        """Fetch all active refresh tokens.

        Returns:
            A list of refresh tokens whose ``revoked_at`` is still ``None``.

        """
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.revoked_at.is_(None))  # ty: ignore[invalid-argument-type]
        )
        return list(result.scalars().all())

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()
