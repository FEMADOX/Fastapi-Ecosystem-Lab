from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from learn_fastapi.src.auth.models import RefreshToken as RefreshTokenORM
from learn_fastapi.src.auth.utils import verify_refresh_token
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.shared.infrastructure.repository import BaseSQLAlchemyRepository
from learn_fastapi.src.users.domain.entities import (
    PersistedUser,
)
from learn_fastapi.src.users.domain.errors import UserDoesntExistError
from learn_fastapi.src.users.infrastructure.mappers import (
    persisted_user_from_orm,
)
from learn_fastapi.src.users.models import User as UserModel
from learn_fastapi.src.utils.repository import bool_to_column


class SQLAlchemyUsersRepository(BaseSQLAlchemyRepository):
    """Repository for managing items using SQLAlchemy."""

    async def get_user_by_id(self, user_id: UserId) -> PersistedUser | None:
        """Fetch a user by ID.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.items),
                selectinload(UserModel.refresh_tokens),
            )
            .where(bool_to_column(UserModel.id == user_id))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None
        return persisted_user_from_orm(orm_user)

    async def get_user_by_email(self, user_email: str) -> PersistedUser | None:
        """Fetch a user by email address.

        Args:
            user_email: The email to search for.

        Returns:
            The matching user or ``None`` if no user exists.

        """
        result = await self.session.execute(
            select(UserModel)
            .options(
                selectinload(UserModel.items),
                selectinload(UserModel.refresh_tokens),
            )
            .where(bool_to_column(UserModel.email == user_email))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None
        return persisted_user_from_orm(orm_user)

    async def get_user_by_refresh_token(
        self, refresh_token: str
    ) -> PersistedUser | None:
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
                selectinload(RefreshTokenORM.user).selectinload(UserModel.items),
                selectinload(RefreshTokenORM.user).selectinload(
                    UserModel.refresh_tokens
                ),
            )
        )
        result = await self.session.scalars(statement)
        for token_record in result.all():
            if verify_refresh_token(refresh_token, token_record.token_hash):
                return persisted_user_from_orm(token_record.user)

        return None

    async def create_user(self, email: str, password_hash: str) -> PersistedUser:
        """Persist a new user.

        Args:
            email: The user's email address.
            password_hash: The Argon2 password hash to store.

        Returns:
            The newly created and refreshed user instance.

        """
        orm_user = UserModel(email=email, password_hash=password_hash)

        self.session.add(orm_user)
        await self.commit()
        await self.session.refresh(orm_user)

        return persisted_user_from_orm(orm_user, False)  # noqa: FBT003

    async def update_user(
        self, user_id: UserId, new_email: str | None, new_password_hash: str | None
    ) -> PersistedUser:
        """Persist user changes and return the refreshed domain instance.

        Args:
            user_id: The user id of the user to update.
            new_email: The new email to persist, if provided.
            new_password_hash: The new password hash to persist, if provided.

        Returns:
            The refreshed user instance after the commit.

        Raises:
            UserDoesntExistError: Raise if user doesn't exist.

        """
        result = await self.session.execute(
            select(UserModel).where(bool_to_column(UserModel.id == user_id))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            raise UserDoesntExistError

        if new_email:
            orm_user.email = new_email

        if new_password_hash:
            orm_user.password_hash = new_password_hash

        await self.commit()
        await self.session.refresh(orm_user)

        return persisted_user_from_orm(orm_user, False)  # noqa: FBT003

    async def delete_user(self, user_id: UserId) -> bool:
        """Delete a user and all related records via cascade.

        Args:
            user_id: The user id of the user to delete.

        Returns:
            bool: True if user deleted successfully else False.

        """
        result = await self.session.execute(
            select(UserModel).where(bool_to_column(UserModel.id == user_id))
        )
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return False

        await self.session.delete(orm_user)
        await self.commit()
        return True
