import contextlib
from dataclasses import dataclass
from datetime import timedelta

from learn_fastapi.src.auth.application.commands import (
    CreateRefreshTokenCommand,
    IssueAccessTokenCommand,
    LoginCommand,
    RevokeRefreshTokenCommand,
    RevokeRefreshTokensCommand,
)
from learn_fastapi.src.auth.application.dto import (
    IssuedAccessToken,
    IssuedRefreshToken,
    LoginResult,
)
from learn_fastapi.src.auth.application.ports import (
    AccessTokenIssuer,
    AuthEventPublisher,
    RefreshTokenGenerator,
    RefreshTokenHasher,
)
from learn_fastapi.src.auth.application.queries import (
    GetRefreshTokenQuery,
    GetUserByRefreshTokenQuery,
)
from learn_fastapi.src.auth.domain.entities import (
    PersistedRefreshToken,
)
from learn_fastapi.src.auth.domain.errors import (
    CredentialsError,
    DoesntExistRefreshTokenError,
    DoesntExistUserError,
)
from learn_fastapi.src.auth.domain.ports import AuthRepository
from learn_fastapi.src.shared.application.security import Clock, PasswordHasher
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.application.commands import RegisterNewUserCommand
from learn_fastapi.src.users.application.use_cases import (
    BaseUsersUseCase,
    GetUserByRefreshTokenUseCase,
    RegisterUserUseCase,
)
from learn_fastapi.src.users.domain.entities import (
    AuthenticatedUser,
    PersistedUser,
)
from learn_fastapi.src.users.domain.errors import (
    UserInactiveError,
)
from learn_fastapi.src.users.domain.value_objects import PasswordHash


@dataclass(slots=True)
class BaseAuthUseCase:
    """Base class for all `auth` app use cases."""

    auth_repository: AuthRepository


class GetRefreshTokenUseCase(BaseAuthUseCase):
    """Use case for retrieving a refresh token by Owner ID."""

    async def execute(self, query: GetRefreshTokenQuery) -> PersistedRefreshToken:
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


@dataclass(slots=True)
class LoginUseCase(BaseUsersUseCase):
    """Use case for logging in a user."""

    password_hasher: PasswordHasher

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
            # The legacy user entity exposes hashes as ``str`` until the users
            # migration publishes its PasswordHash-aware entity.
            or not self.password_hasher.verify(
                command.password, PasswordHash(user.password_hash)
            )
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


@dataclass(slots=True)
class IssueAccessTokenUseCase:
    """Use case for issuing an access token for an authenticated user."""

    token_issuer: AccessTokenIssuer
    clock: Clock
    expires_in: timedelta

    async def execute(self, command: IssueAccessTokenCommand) -> IssuedAccessToken:
        """Issue an access token with a deterministic expiration boundary.

        Returns:
            IssuedAccessToken: Access Token data.

        """
        expires_at = self.clock.now() + self.expires_in
        return IssuedAccessToken(
            value=self.token_issuer.issue(command.owner_id, expires_at),
            expires_at=expires_at,
            expires_in=int(self.expires_in.total_seconds()),
        )


@dataclass(slots=True)
class CreateRefreshTokenUseCase(BaseAuthUseCase):
    """Use case for creating a refresh token."""

    token_generator: RefreshTokenGenerator
    token_hasher: RefreshTokenHasher
    clock: Clock
    expires_in: timedelta

    async def execute(self, command: CreateRefreshTokenCommand) -> IssuedRefreshToken:
        """Execute the use case.

        Returns:
            The raw token for the client and its expiration metadata.

        """
        raw_token = self.token_generator.generate()
        expires_at = self.clock.now() + self.expires_in
        await self.auth_repository.create_refresh_token(
            command.owner_id,
            self.token_hasher.hash(raw_token),
            expires_at,
        )
        return IssuedRefreshToken(
            value=raw_token,
            expires_at=expires_at,
            expires_in=int(self.expires_in.total_seconds()),
        )


class RevokeRefreshTokensUseCase(BaseAuthUseCase):
    """Use case for revoking refresh tokens."""

    async def execute(self, command: RevokeRefreshTokensCommand) -> None:
        """Execute the use case."""
        await self.auth_repository.revoke_refresh_tokens(command.owner_id)


class RevokeRefreshTokenUseCase(BaseAuthUseCase):
    """Use case for revoking a refresh token."""

    async def execute(self, command: RevokeRefreshTokenCommand) -> None:
        """Execute the use case."""
        await self.auth_repository.revoke_refresh_token(
            command.token, command.token_raw
        )


# ---------------------------------------------------------------------------
# Composite use cases (orchestrate primitives + publish events)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class FullLoginUseCase:
    """Orchestrates authentication, token issuance and event publishing."""

    login: LoginUseCase
    issue_access_token: IssueAccessTokenUseCase
    get_refresh_token: GetRefreshTokenUseCase
    revoke_refresh_tokens: RevokeRefreshTokensUseCase
    create_refresh_token: CreateRefreshTokenUseCase
    event_publisher: AuthEventPublisher

    async def execute(self, command: LoginCommand) -> LoginResult:
        user = await self.login.execute(command)

        access_token = await self.issue_access_token.execute(
            IssueAccessTokenCommand(user.id)
        )

        with contextlib.suppress(DoesntExistRefreshTokenError):
            await self.get_refresh_token.execute(GetRefreshTokenQuery(user.id))
            await self.revoke_refresh_tokens.execute(
                RevokeRefreshTokensCommand(user.id)
            )

        refresh_token = await self.create_refresh_token.execute(
            CreateRefreshTokenCommand(user.id)
        )

        await self.event_publisher.auth_logged_in(user.id)

        return LoginResult(
            access_token=access_token.value,
            access_expires_in=access_token.expires_in,
            refresh_token_raw=refresh_token.value,
            refresh_expires_in=refresh_token.expires_in,
            user_id=user.id,
        )


@dataclass(slots=True)
class RefreshAccessTokenUseCase:
    """Validate a raw refresh token and issue a new access token."""

    get_user_by_refresh_token: GetUserByRefreshTokenUseCase
    issue_access_token: IssueAccessTokenUseCase

    async def execute(self, query: GetUserByRefreshTokenQuery) -> IssuedAccessToken:
        user = await self.get_user_by_refresh_token.execute(query)
        return await self.issue_access_token.execute(IssueAccessTokenCommand(user.id))


@dataclass(slots=True)
class LogoutUseCase:
    """Revoke the refresh token and publish a logout event."""

    get_refresh_token: GetRefreshTokenUseCase
    revoke_refresh_token: RevokeRefreshTokenUseCase
    event_publisher: AuthEventPublisher

    async def execute(self, owner_id: UserId, refresh_token_raw: str | None) -> None:
        if refresh_token_raw:
            try:
                token_record = await self.get_refresh_token.execute(
                    GetRefreshTokenQuery(owner_id)
                )
                await self.revoke_refresh_token.execute(
                    RevokeRefreshTokenCommand(token_record, refresh_token_raw)
                )
            except DoesntExistRefreshTokenError:
                pass

        await self.event_publisher.auth_logged_out(owner_id)


@dataclass(slots=True)
class RegisterAccountUseCase:
    """Register a new user account and publish an auth event."""

    register_user: RegisterUserUseCase
    event_publisher: AuthEventPublisher

    async def execute(self, command: RegisterNewUserCommand) -> PersistedUser:
        new_user = await self.register_user.execute(command)
        await self.event_publisher.auth_registered(new_user)
        return new_user
