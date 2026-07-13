from learn_fastapi.src.auth.application.commands import RegisterNewUserCommand
from learn_fastapi.src.auth.application.queries import GetUserByRefreshTokenQuery
from learn_fastapi.src.auth.domain.errors import DoesntExistUserError
from learn_fastapi.src.auth.utils import hash_password
from learn_fastapi.src.users.application.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
)
from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.domain.errors import (
    UserAlreadyExistsError,
    UserDoesntExistError,
)
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository


class BaseUseCase:
    """Base class for all use cases."""

    def __init__(self, users_repository: SQLAlchemyUsersRepository) -> None:
        """Initialize the use case with the user repository."""
        self.users_repository = users_repository


class GetUserByIdUseCase(BaseUseCase):
    """Use case for retrieving a user by its ID."""

    async def execute(self, query: GetUserByIdQuery) -> PersistedUser:
        """Execute the use case.

        Returns:
            The requested user.

        Raises:
            UserDoesntExistError: If the user doesn't exist.

        """
        user = await self.users_repository.get_user_by_id(query.user_id)
        if not user:
            raise UserDoesntExistError
        return user


class GetUserByEmailUseCase(BaseUseCase):
    """Use case for retrieving a user by its email."""

    async def execute(self, query: GetUserByEmailQuery) -> PersistedUser:
        """Execute the use case.

        Returns:
            The requested user.

        Raises:
            UserDoesntExistError: If the user doesn't exist.

        """
        user = await self.users_repository.get_user_by_email(query.user_email)
        if not user:
            raise UserDoesntExistError
        return user


class GetUserByRefreshTokenUseCase(BaseUseCase):
    """Use case for retrieving a User through the refresh token."""

    async def execute(self, query: GetUserByRefreshTokenQuery) -> PersistedUser:
        """Execute the use case.

        Returns:
            UserDomain: The requested user.

        Raises:
            DoesntExistUserError: If the user doesn't exist.

        """
        user = await self.users_repository.get_user_by_refresh_token(
            query.refresh_token
        )
        if not user:
            raise DoesntExistUserError
        return user


class RegisterUserUseCase(BaseUseCase):
    """Use case for registering a user."""

    async def execute(self, command: RegisterNewUserCommand) -> PersistedUser:
        """Execute the use case.

        Returns:
            UserDomain: The registered user.

        Raises:
            DoesntExistUserError: If the user doesn't exist.

        """
        existing_user = await self.users_repository.get_user_by_email(command.email)
        if existing_user:
            raise UserAlreadyExistsError

        password_hash = hash_password(command.password)

        return await self.users_repository.create_user(
            command.email,
            password_hash,
        )
