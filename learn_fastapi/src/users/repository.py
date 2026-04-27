from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.database import AsyncSessionDep

from .models import User


class UsersRepository:
    """Repository class for user account ORM operations."""

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
        result = await self.session.execute(select(User).where(User.id == user_id))  # ty:ignore[invalid-argument-type]
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(select(User).where(User.email == email))  # ty:ignore[invalid-argument-type]
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> User:
        """Persist in-place changes to a user and return the refreshed instance.

        Args:
            user: The user instance with updated fields already applied.

        Returns:
            The refreshed user instance after the commit.

        """
        await self.commit()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user: User) -> None:
        """Delete a user and all related records via cascade.

        Args:
            user: The user instance to delete.

        """
        await self.session.delete(user)
        await self.commit()
