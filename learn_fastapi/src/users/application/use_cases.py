from dataclasses import dataclass

from learn_fastapi.src.auth.application.queries import GetUserByRefreshTokenQuery
from learn_fastapi.src.auth.domain.errors import DoesntExistUserError
from learn_fastapi.src.shared.application.dto import AuthenticatedAccount, CurrentActor
from learn_fastapi.src.shared.application.security import PasswordHasher
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.application.commands import (
    DeleteAccountCommand,
    RegisterNewUserCommand,
    UpdateUserCommand,
)
from learn_fastapi.src.users.application.ports import UsersEventPublisher
from learn_fastapi.src.users.application.queries import (
    GetAccountQuery,
    GetUserByEmailQuery,
    GetUserByIdQuery,
)
from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.domain.errors import (
    IncorrectPasswordError,
    OnlyOwnerIsAuthorizedError,
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


@dataclass(slots=True)
class GetAccountUseCase:
    """Retrieve an account after enforcing actor authorization."""

    get_user_by_id: GetUserByIdUseCase

    async def execute(self, query: GetAccountQuery) -> PersistedUser:
        """Return the requested account when the actor is authorized.

        Raises:
            OnlyOwnerIsAuthorizedError: If the actor cannot read the account.
            UserDoesntExistError: If the requested account does not exist.

        """
        _authorize_account(query.actor, query.user_id)
        return await self.get_user_by_id.execute(GetUserByIdQuery(query.user_id))


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


@dataclass(slots=True)
class RegisterUserUseCase(BaseUsersUseCase):
    """Use case for registering a user."""

    password_hasher: PasswordHasher

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

        password_hash = self.password_hasher.hash(command.password)

        return await self.users_repository.create_user(
            command.email,
            password_hash,
        )


@dataclass(slots=True)
class UpdateUserUseCase(BaseUsersUseCase):
    """Use case for updating a user."""

    password_hasher: PasswordHasher
    event_publisher: UsersEventPublisher

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
            OnlyOwnerIsAuthorizedError: If the actor cannot update the account.
            IncorrectPasswordError: If the actor password is incorrect.
            UserDoesntExistError: Raised when the user doesn't exist.
            UserAlreadyExistsError: Raised when account with that email already exist.

        """
        _authorize_account(command.actor.to_actor(), command.user_id)
        _verify_password(
            command.current_password,
            command.actor,
            self.password_hasher,
        )

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
            password_hash = self.password_hasher.hash(command.new_password)
            changed_fields.append("password")

        updated_user = await self.users_repository.update_user(
            command.user_id, command.new_email, password_hash
        )

        await self.event_publisher.account_updated(updated_user, changed_fields)

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


@dataclass(slots=True)
class DeleteAccountUseCase:
    """Fetch the user, delete, and publish the account_deleted event."""

    get_user_by_id: GetUserByIdUseCase
    delete_user: DeleteUserUseCase
    event_publisher: UsersEventPublisher
    password_hasher: PasswordHasher

    async def execute(self, command: DeleteAccountCommand) -> None:
        """Authorize, verify, delete, and publish the account event.

        Raises:
            OnlyOwnerIsAuthorizedError: If the actor cannot delete the account.
            IncorrectPasswordError: If the actor password is incorrect.
            UserDoesntExistError: If the requested account does not exist.

        """
        _authorize_account(command.actor.to_actor(), command.user_id)
        _verify_password(
            command.current_password,
            command.actor,
            self.password_hasher,
        )
        user_to_delete = await self.get_user_by_id.execute(
            GetUserByIdQuery(command.user_id)
        )
        await self.delete_user.execute(command.user_id)
        await self.event_publisher.account_deleted(user_to_delete)


def _authorize_account(actor: CurrentActor, user_id: UserId) -> None:
    """Enforce owner-or-superuser access for account operations."""
    # Keeping this rule in application makes it consistent across HTTP and future APIs.
    if not actor.is_superuser and actor.id != user_id:
        raise OnlyOwnerIsAuthorizedError


def _verify_password(
    password: str,
    actor: AuthenticatedAccount,
    password_hasher: PasswordHasher,
) -> None:
    """Verify the authenticated actor's current password."""
    if not password_hasher.verify(password, actor.password_hash):
        raise IncorrectPasswordError
