import secrets
from datetime import UTC, datetime
from uuid import UUID

from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import Response

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.schema import UserCreate
from learn_fastapi.src.utils.exceptions import (
    email_already_registered_exception,
    user_inactive_exception,
)
from learn_fastapi.src.utils.service import BaseService

from .config import auth_config
from .exceptions import (
    credentials_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
)
from .repository import AuthRepository
from .schema import Token, TokenData, TokenV2
from .utils import (
    clear_auth_cookies,
    create_access_token,
    generate_refresh_token,
    get_refresh_token_expiration,
    hash_password,
    hash_refresh_token,
    set_auth_cookies,
    verify_password,
    verify_refresh_token,
)


async def _login(
    repository: AuthRepository,
    form_data: OAuth2PasswordRequestForm,
    response: Response,
) -> tuple[str, str, str, UUID]:
    """Authenticate a user and mint new access/refresh/csrf tokens.

    Args:
        repository: The AuthRepository instance to use for database operations.
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
    user = await repository.get_user_by_email(form_data.username.lower())

    if not user or not verify_password(form_data.password, user.password_hash):
        raise credentials_exception()

    if not user.is_active:
        raise user_inactive_exception()

    user_id = user.id

    access_token = create_access_token(TokenData(sub=str(user_id)))
    refresh_token_raw = generate_refresh_token()
    refresh_token_hashed = hash_refresh_token(refresh_token_raw)

    user_refresh_token = await repository.get_refresh_token(user_id)
    if user_refresh_token:
        await repository.revoke_refresh_token(user_id)

    csrf_token = secrets.token_urlsafe(24)

    await repository.create_refresh_token(
        user_id=user_id,
        token_hash=refresh_token_hashed,
        expires_at=get_refresh_token_expiration(),
    )

    set_auth_cookies(response, refresh_token_raw, csrf_token)

    return access_token, refresh_token_raw, csrf_token, user_id


class AuthService(BaseService):
    """Service class for auth business logic."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository: AuthRepository = AuthRepository(session)

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user account.

        Args:
            user_data: The user registration payload.

        Returns:
            The newly created user instance.

        Raises:
            email_already_registered_exception: If the email already exists.

        """
        existing_user = await self.repository.get_user_by_email(user_data.email)
        if existing_user is not None:
            raise email_already_registered_exception()

        user = await self.repository.create_user(
            email=str(user_data.email),
            password_hash=hash_password(user_data.password),
        )

        await self._broadcast_sse_event(
            "auth.registered",
            {
                "user_id": str(user.id),
                "email": user.email
            },
        )

        return user

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
            self.repository, form_data, response
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

        user = await self.repository.get_user_from_refresh_token(refresh_token_raw)
        if not user:
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
            token_record = await self.repository.get_refresh_token(user.id)
            if token_record and verify_refresh_token(
                refresh_token_raw, token_record.token_hash
            ):
                token_record.revoked_at = datetime.now(tz=UTC)
                await self.repository.commit()

        clear_auth_cookies(response)

        await self._broadcast_sse_event(
            "auth.logged_out",
            {"user_id": str(user.id)},
            user_id=user.id,
        )


class AuthServiceV2(BaseService):
    """Service class for auth business logic for API Version 2."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository: AuthRepository = AuthRepository(session)

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
            self.repository, form_data, response
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
