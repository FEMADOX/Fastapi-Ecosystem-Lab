from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.infrastructure.mappers import user_from_orm
from learn_fastapi.src.users.models import User as UserORM
from learn_fastapi.src.utils.repository import bool_to_column


class SQLAlchemyUserRepository:
    """Repository for managing items using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous SQLAlchemy session."""
        self.session = session

    async def get_user_by_id(self, user_id: UserId) -> UserDomain | None:
        """Fetch a user by primary key.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(UserORM)
            .options(
                selectinload(UserORM.items),
                selectinload(UserORM.refresh_tokens),
            )
            .where(bool_to_column(UserORM.id == user_id))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None
        return user_from_orm(orm_user)

    async def get_user_by_email(self, user_email: str) -> UserDomain | None:
        """Fetch a user by email address.

        Args:
            user_email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(UserORM)
            .options(
                selectinload(UserORM.items),
                selectinload(UserORM.refresh_tokens),
            )
            .where(bool_to_column(UserORM.email == user_email))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None
        return user_from_orm(orm_user)
