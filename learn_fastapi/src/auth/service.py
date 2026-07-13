import contextlib
import secrets
from uuid import UUID

from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import Response

from learn_fastapi.src.auth.application.commands import (
    CreateRefreshTokenCommand,
    LoginCommand,
    RegisterNewUserCommand,
    RevokeRefreshTokenCommand,
    RevokeRefreshTokensCommand,
)
from learn_fastapi.src.auth.application.queries import (
    GetRefreshTokenQuery,
    GetUserByRefreshTokenQuery,
)
from learn_fastapi.src.auth.application.use_cases import (
    CreateRefreshTokenUseCase,
    GetRefreshTokenUseCase,
    LoginUseCase,
    RevokeRefreshTokensUseCase,
    RevokeRefreshTokenUseCase,
)
from learn_fastapi.src.auth.domain.errors import (
    CredentialsError,
    DoesntExistRefreshTokenError,
    DoesntExistUserError,
)
from learn_fastapi.src.auth.presentation.exceptions import (
    credentials_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
)
from learn_fastapi.src.shared.presentation.exceptions import (
    email_already_registered_exception,
    user_inactive_exception,
)
from learn_fastapi.src.users.application.use_cases import (
    GetUserByEmailUseCase,
    GetUserByRefreshTokenUseCase,
    RegisterUserUseCase,
)
from learn_fastapi.src.users.domain.errors import (
    UserAlreadyExistsError,
    UserInactiveError,
)
from learn_fastapi.src.users.infrastructure.mappers import persisted_user_to_schema
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.schema import UserCreate, UserResponse
from learn_fastapi.src.utils.service import BaseService

from .config import auth_config
from .schema import Token, TokenData, TokenV2
from .utils import (
    clear_auth_cookies,
    create_access_token,
    generate_refresh_token,
    get_refresh_token_expiration,
    hash_refresh_token,
    set_auth_cookies,
)


async def _login(
    login_use_case: LoginUseCase,
    get_refresh_token_use_case: GetRefreshTokenUseCase,
    create_refresh_token_use_case: CreateRefreshTokenUseCase,
    revoke_refresh_tokens_use_case: RevokeRefreshTokensUseCase,
    form_data: OAuth2PasswordRequestForm,
    response: Response,
) -> tuple[str, str, str, UUID]:
    """Authenticate a user and mint new access/refresh/csrf tokens.

    Args:
        login_use_case: The use case for logging in a user.
        get_refresh_token_use_case:
            The use case for retrieving a refresh token by the owner id.
        create_refresh_token_use_case:
            The use case for creating a refresh token.
        revoke_refresh_tokens_use_case:
            The use case for revoking all the active refresh token.
        form_data: OAuth2 login form data.
        response: Response object used to set auth cookies.

    Returns:
        (access_token, refresh_token_raw, csrf_token, user_id):
            access_token: JWT access token string
            refresh_token_raw: The raw (unhashed) refresh token string
            csrf_token: CSRF token string
            user_id: UUID of the authenticated user

    Raises:
        credentials_exception: If the credentials are invalid.
        user_inactive_exception: If the user account is inactive.

    """
    try:
        user = await login_use_case.execute(
            LoginCommand(email=form_data.username.lower(), password=form_data.password)
        )
    except DoesntExistUserError as exc:
        raise credentials_exception() from exc
    except CredentialsError as exc:
        raise credentials_exception() from exc
    except UserInactiveError as exc:
        raise user_inactive_exception() from exc

    user_id = user.id

    access_token = create_access_token(TokenData(sub=str(user_id)))
    refresh_token_raw = generate_refresh_token()
    refresh_token_hashed = hash_refresh_token(refresh_token_raw)

    with contextlib.suppress(DoesntExistRefreshTokenError):
        await get_refresh_token_use_case.execute(GetRefreshTokenQuery(user_id))
        await revoke_refresh_tokens_use_case.execute(
            RevokeRefreshTokensCommand(user_id)
        )

    csrf_token = secrets.token_urlsafe(24)

    await create_refresh_token_use_case.execute(
        CreateRefreshTokenCommand(
            user_id, refresh_token_hashed, get_refresh_token_expiration()
        )
    )

    set_auth_cookies(response, refresh_token_raw, csrf_token)

    return access_token, refresh_token_raw, csrf_token, user_id


class BaseAuthService(BaseService):
    """Base service class for auth business logic."""

    def __init__(
        self,
        get_refresh_token_use_case: GetRefreshTokenUseCase,
        get_user_by_email_use_case: GetUserByEmailUseCase,
        get_user_by_refresh_token_use_case: GetUserByRefreshTokenUseCase,
        login_use_case: LoginUseCase,
        register_user_use_case: RegisterUserUseCase,
        create_refresh_token_use_case: CreateRefreshTokenUseCase,
        revoke_refresh_tokens_use_case: RevokeRefreshTokensUseCase,
        revoke_refresh_token_use_case: RevokeRefreshTokenUseCase,
    ) -> None:
        """Initialize the service with an async database session."""
        self.get_refresh_token_use_case = get_refresh_token_use_case
        self.get_user_by_email_use_case = get_user_by_email_use_case
        self.get_user_by_refresh_token_use_case = get_user_by_refresh_token_use_case
        self.login_use_case = login_use_case
        self.register_user_use_case = register_user_use_case
        self.create_refresh_token_use_case = create_refresh_token_use_case
        self.revoke_refresh_tokens_use_case = revoke_refresh_tokens_use_case
        self.revoke_refresh_token_use_case = revoke_refresh_token_use_case


class AuthService(BaseAuthService):
    """Service class for auth business logic."""

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user account.

        Args:
            user_data: The user registration payload.

        Returns:
            The newly created user instance.

        Raises:
            email_already_registered_exception: If the email already exists.

        """
        try:
            new_user = await self.register_user_use_case.execute(
                RegisterNewUserCommand(
                    user_data.email,
                    user_data.password,
                )
            )
        except UserAlreadyExistsError as exc:
            raise email_already_registered_exception() from exc

        schema = persisted_user_to_schema(new_user)

        await self._broadcast_sse_event(
            "auth.registered",
            {"user_id": str(new_user.id), "email": new_user.email},
        )

        return schema

    async def login(
        self,
        form_data: OAuth2PasswordRequestForm,
        response: Response,
    ) -> Token:
        """Authenticate a user and mint new access/refresh tokens.

        Args:
            form_data: OAuth2 login form data.
            response: Response object used to set auth cookies.

        Returns:
            A token response with access and CSRF tokens.

        """
        access_token, _, csrf_token, user_id = await _login(
            self.login_use_case,
            self.get_refresh_token_use_case,
            self.create_refresh_token_use_case,
            self.revoke_refresh_tokens_use_case,
            form_data,
            response,
        )

        await self._broadcast_sse_event(
            "auth.logged_in",
            {"user_id": str(user_id)},
            user_id=user_id,
        )

        return Token(
            access_token=access_token,
            expires_in=int(auth_config.access_token_expire.total_seconds()),
            csrf_token=csrf_token,
        )

    async def refresh_token(
        self,
        request: Request,
        x_csrf_token: str,
    ) -> Token:
        """Rotate refresh a new access token.

        Args:
            request: Request used to read cookies.
            x_csrf_token: CSRF token provided in the request header.

        Returns:
            A new token response.

        Raises:
            invalid_refresh_token_exception: If the refresh token is invalid.
            invalid_refresh_or_csrf_token_exception: If CSRF/cookie validation fails.

        """
        refresh_token_raw = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")

        if (
            not refresh_token_raw
            or not csrf_token
            or not x_csrf_token
            or x_csrf_token != csrf_token
        ):
            raise invalid_refresh_or_csrf_token_exception()

        query = GetUserByRefreshTokenQuery(refresh_token_raw)
        try:
            user = await self.get_user_by_refresh_token_use_case.execute(query)
        except DoesntExistUserError as exc:
            raise invalid_refresh_token_exception() from exc

        if user.id is None:
            raise invalid_refresh_token_exception()

        access_token = create_access_token(TokenData(sub=str(user.id)))

        return Token(
            access_token=access_token,
            expires_in=int(auth_config.access_token_expire.total_seconds()),
            csrf_token=csrf_token,
        )

    async def logout(
        self,
        user: User,
        request: Request,
        response: Response,
        x_csrf_token: str | None,
    ) -> None:
        """Revoke the current refresh token and clear auth cookies.

        Args:
            user: The current authenticated user.
            request: Request used to read auth cookies.
            response: Response used to clear cookies.
            x_csrf_token: CSRF token header value.

        """
        refresh_token_raw = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")

        if (
            refresh_token_raw
            and csrf_token
            and x_csrf_token
            and csrf_token == x_csrf_token
        ):
            try:
                token_record = await self.get_refresh_token_use_case.execute(
                    GetRefreshTokenQuery(user.id)
                )
                await self.revoke_refresh_token_use_case.execute(
                    RevokeRefreshTokenCommand(token_record, refresh_token_raw)
                )
            except DoesntExistRefreshTokenError:
                pass

        clear_auth_cookies(response)

        await self._broadcast_sse_event(
            "auth.logged_out",
            {"user_id": str(user.id)},
            user_id=user.id,
        )


class AuthServiceV2(BaseAuthService):
    """Service class for auth business logic for API Version 2."""

    async def login(
        self,
        form_data: OAuth2PasswordRequestForm,
        response: Response,
    ) -> TokenV2:
        """Authenticate a user and mint new access/refresh tokens but version 2.

        Args:
            form_data: OAuth2 login form data.
            response: Response object used to set auth cookies.

        Returns:
            TokenV2:
                A token response with:
                - access_token (plus access_expire_in)
                - refresh_token (plus refresh_expires_in)
                - CSRF

        """
        access_token, refresh_token_raw, csrf_token, user_id = await _login(
            self.login_use_case,
            self.get_refresh_token_use_case,
            self.create_refresh_token_use_case,
            self.revoke_refresh_tokens_use_case,
            form_data,
            response,
        )

        await self._broadcast_sse_event(
            "auth.logged_in",
            {"user_id": str(user_id)},
            user_id=user_id,
        )

        return TokenV2(
            access_token=access_token,
            access_expires_in=int(auth_config.access_token_expire.total_seconds()),
            refresh_token=refresh_token_raw,
            refresh_expires_in=int(auth_config.refresh_token_expire.total_seconds()),
            csrf_token=csrf_token,
        )
