from uuid import UUID

from sqlalchemy import select

from learn_fastapi.src.utils.repository import BaseRepository, bool_to_column

from .models import User


class UsersRepository(BaseRepository):
    """Repository class for user account ORM operations."""

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by primary key.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(User).where(bool_to_column(User.id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch a user by email address.

        Args:
            email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(User).where(bool_to_column(User.email == email))
        )
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
