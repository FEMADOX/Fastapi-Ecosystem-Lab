from dataclasses import dataclass

from learn_fastapi.src.auth.application.queries import GetUserByRefreshTokenQuery
from learn_fastapi.src.auth.domain.errors import DoesntExistUserError
from learn_fastapi.src.auth.utils import hash_password
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.application.commands import (
    RegisterNewUserCommand,
    UpdateUserCommand,
)
from learn_fastapi.src.users.application.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
)
from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.domain.errors import (
    UserAlreadyExistsError,
    UserDoesntExistError,
)
from learn_fastapi.src.users.domain.ports import UsersRepository


@dataclass(slots=True)
class BaseUsersUseCase:
    """Base class for all `users` app use cases."""

    users_repository: UsersRepository


class GetUserByIdUseCase(BaseUsersUseCase):
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


class GetUserByEmailUseCase(BaseUsersUseCase):
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


class GetUserByRefreshTokenUseCase(BaseUsersUseCase):
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


class RegisterUserUseCase(BaseUsersUseCase):
    """Use case for registering a user."""

    async def execute(self, command: RegisterNewUserCommand) -> PersistedUser:
        """Execute the use case.

        Returns:
            UserDomain: The registered user.

        Raises:
            UserAlreadyExistsError: Raised when account with that email already exist.

        """
        existing_user = await self.users_repository.get_user_by_email(command.email)
        if existing_user:
            raise UserAlreadyExistsError

        password_hash = hash_password(command.password)

        return await self.users_repository.create_user(
            command.email,
            password_hash,
        )


class UpdateUserUseCase(BaseUsersUseCase):
    """Use case for updating a user."""

    async def execute(
        self, command: UpdateUserCommand
    ) -> tuple[PersistedUser, list[str]]:
        """Execute the use case.

        Args:
            command: An instance of `UpdateUserCommand`.

        Returns:
            PersistedUser: The persisted user.
            changed_fields: A list of the fields to update.

        Raises:
            UserDoesntExistError: Raised when the user doesn't exist.
            UserAlreadyExistsError: Raised when account with that email already exist.

        """
        user = await self.users_repository.get_user_by_id(command.user_id)
        if not user:
            raise UserDoesntExistError

        changed_fields = []

        if command.new_email:
            existing_user = await self.users_repository.get_user_by_email(
                command.new_email
            )
            if existing_user and existing_user.id != command.user_id:
                raise UserAlreadyExistsError

            changed_fields.append("email")

        password_hash = None
        if command.new_password:
            password_hash = hash_password(command.new_password)
            changed_fields.append("password")

        updated_user = await self.users_repository.update_user(
            command.user_id, command.new_email, password_hash
        )

        return updated_user, changed_fields


class DeleteUserUseCase(BaseUsersUseCase):
    """Use case for deleting a user."""

    async def execute(self, user_id: UserId) -> None:
        """Execute the use case.

        Args:
            user_id: The user id of the user to delete.

        Raises:
            UserDoesntExistError: Raised when the user doesn't exist.

        """
        if not await self.users_repository.delete_user(user_id):
            raise UserDoesntExistError
