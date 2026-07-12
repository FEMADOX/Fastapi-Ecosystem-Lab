from learn_fastapi.src.auth.application.commands import (
    CreateRefreshTokenCommand,
    LoginCommand,
    RevokeRefreshTokenCommand,
    RevokeRefreshTokensCommand,
)
from learn_fastapi.src.auth.application.queries import (
    GetRefreshTokenQuery,
    GetUserFromRefreshTokenQuery,
)
from learn_fastapi.src.auth.domain.entities import RefreshToken as RefreshTokenDomain
from learn_fastapi.src.auth.domain.errors import (
    CredentialsError,
    DoesntExistRefreshTokenError,
    DoesntExistUserError,
)
from learn_fastapi.src.auth.domain.ports import AuthRepository
from learn_fastapi.src.auth.utils import verify_password
from learn_fastapi.src.users.domain.entities import (
    AuthenticatedUser,
)
from learn_fastapi.src.users.domain.entities import (
    User as UserDomain,
)
from learn_fastapi.src.users.domain.errors import UserInactiveError
from learn_fastapi.src.users.domain.ports import UsersRepository


class BaseUseCase:
    """Base class for all use cases."""

    def __init__(self, auth_repository: AuthRepository) -> None:
        """Initialize the use case with the item repository."""
        self.auth_repository = auth_repository


class GetRefreshTokenUseCase(BaseUseCase):
    """Use case for retrieving a refresh token by Owner ID."""

    async def execute(self, query: GetRefreshTokenQuery) -> RefreshTokenDomain:
        """Execute the use case.

        Returns:
            RefreshToken: The requested refresh token.

        Raises:
            DoesntExistRefreshTokenError: If the refresh token doesn't exist.

        """
        refresh_token = await self.auth_repository.get_refresh_token(query.owner_id)
        if not refresh_token:
            raise DoesntExistRefreshTokenError
        return refresh_token


class GetUserFromRefreshTokenUseCase(BaseUseCase):
    """Use case for retrieving a User through the refresh token."""

    async def execute(self, query: GetUserFromRefreshTokenQuery) -> UserDomain:
        """Execute the use case.

        Returns:
            UserDomain: The requested user.

        Raises:
            DoesntExistUserError: If the user doesn't exist.

        """
        user = await self.auth_repository.get_user_from_refresh_token(
            query.refresh_token
        )
        if not user:
            raise DoesntExistUserError
        return user


class LoginUseCase:
    """Use case for logging in a user."""

    def __init__(self, users_repository: UsersRepository) -> None:
        """Initialize the use case with the user repository."""
        self.users_repository = users_repository

    async def execute(self, command: LoginCommand) -> AuthenticatedUser:
        """Execute the use case.

        Returns:
            AuthenticatedUser: The requested user.

        Raises:
            DoesntExistUserError: If the user doesn't exist.
            CredentialsError: If the provided credentials are invalid.
            UserInactiveError: If the user account is inactive.

        """
        user = await self.users_repository.get_user_by_email(command.email)

        if not user:
            raise DoesntExistUserError

        if (
            not user.id
            or not user.password_hash
            or not verify_password(command.password, user.password_hash)
        ):
            raise CredentialsError

        if not user.is_active:
            raise UserInactiveError

        return AuthenticatedUser(
            id=user.id,
            items_ids=user.items_ids,
            refresh_tokens_ids=user.refresh_tokens_ids,
            email=user.email,
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


class CreateRefreshTokenUseCase(BaseUseCase):
    """Use case for creating a refresh token."""

    async def execute(self, command: CreateRefreshTokenCommand) -> RefreshTokenDomain:
        """Execute the use case.

        Returns:
            RefreshToken: The created refresh token.

        """
        return await self.auth_repository.create_refresh_token(
            command.owner_id, command.token_hash, command.expires_in
        )


class RevokeRefreshTokensUseCase(BaseUseCase):
    """Use case for revoking refresh tokens."""

    async def execute(self, command: RevokeRefreshTokensCommand) -> None:
        """Execute the use case."""
        await self.auth_repository.revoke_refresh_tokens(command.owner_id)


class RevokeRefreshTokenUseCase(BaseUseCase):
    """Use case for revoking a refresh token."""

    async def execute(self, command: RevokeRefreshTokenCommand) -> None:
        """Execute the use case."""
        await self.auth_repository.revoke_refresh_token(
            command.token, command.token_raw
        )
