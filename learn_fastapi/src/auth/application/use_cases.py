from learn_fastapi.src.auth.application.commands import LoginCommand
from learn_fastapi.src.auth.application.queries import (
    GetRefreshTokenQuery,
    GetUserFromRefreshTokenQuery,
)
from learn_fastapi.src.auth.domain.entities import RefreshToken
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
from learn_fastapi.src.users.domain.ports import UserRepository


class BaseUseCase:
    """Base class for all use cases."""

    def __init__(self, auth_repository: AuthRepository) -> None:
        """Initialize the use case with the item repository."""
        self.auth_repository = auth_repository


class GetRefreshTokenUseCase(BaseUseCase):
    """Use case for retrieving a refresh token by Owner ID."""

    async def execute(self, query: GetRefreshTokenQuery) -> RefreshToken:
        """Execute the use case.

        Returns:
            The requested refresh token.

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
            The requested user.

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

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the use case with the user repository."""
        self.user_repository = user_repository

    async def execute(self, command: LoginCommand) -> AuthenticatedUser:
        """Execute the use case.

        Returns:
            The requested user.

        Raises:
            DoesntExistUserError: If the user doesn't exist.
            CredentialsError: If the provided credentials are invalid.
            UserInactiveError: If the user account is inactive.

        """
        user = await self.user_repository.get_user_by_email(command.email)

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
