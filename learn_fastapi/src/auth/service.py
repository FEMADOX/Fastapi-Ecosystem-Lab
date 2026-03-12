import secrets
from datetime import UTC, datetime

from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import Response

from learn_fastapi.src.database import AsyncSessionDep

from .config import auth_config
from .exceptions import (
    credentials_exception,
    email_already_registered_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)
from .models import User
from .repository import AuthRepository
from .schema import Token, TokenData, UserCreate
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


class AuthService:
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
            raise email_already_registered_exception

        return await self.repository.create_user(
            email=str(user_data.email),
            password_hash=hash_password(user_data.password),
        )

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

        Raises:
            credentials_exception: If the credentials are invalid.
            user_inactive_exception: If the user account is inactive.

        """
        user = await self.repository.get_user_by_email(form_data.username.lower())

        if not user or not verify_password(form_data.password, user.password_hash):
            raise credentials_exception

        if not user.is_active:
            raise user_inactive_exception

        access_token = create_access_token(TokenData(sub=str(user.id)))
        refresh_token_raw = generate_refresh_token()
        refresh_token_hashed = hash_refresh_token(refresh_token_raw)

        await self.repository.create_refresh_token(
            user_id=user.id,
            token_hash=refresh_token_hashed,
            expires_at=get_refresh_token_expiration(),
        )

        csrf_token = secrets.token_urlsafe(24)
        set_auth_cookies(response, refresh_token_raw, csrf_token)

        return Token(
            access_token=access_token,
            expires_in=int(auth_config.access_token_expire.total_seconds()),
            csrf_token=csrf_token,
        )

    async def refresh_token(
        self,
        request: Request,
        response: Response,
        x_csrf_token: str,
    ) -> Token:
        """Rotate refresh token and issue a new access token.

        Args:
            request: Request used to read cookies.
            response: Response used to write rotated cookies.
            x_csrf_token: CSRF token provided in the request header.

        Returns:
            A new token response.

        Raises:
            invalid_refresh_or_csrf_token_exception: If CSRF/cookie validation fails.
            invalid_refresh_token_exception: If the refresh token is invalid or expired.
            user_doesnt_exist_exception: If the refresh token's user no longer exists.
            user_inactive_exception: If the user is inactive.

        """
        refresh_token_raw = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")

        if (
            not refresh_token_raw
            or not csrf_token
            or not x_csrf_token
            or x_csrf_token != csrf_token
        ):
            raise invalid_refresh_or_csrf_token_exception

        valid_tokens = await self.repository.get_valid_refresh_tokens(
            datetime.now(tz=UTC)
        )

        matching_token = next(
            (
                token_record
                for token_record in valid_tokens
                if verify_refresh_token(refresh_token_raw, token_record.token_hash)
            ),
            None,
        )
        if not matching_token:
            raise invalid_refresh_token_exception

        user = await self.repository.get_user_by_id(matching_token.user_id)
        if not user:
            raise user_doesnt_exist_exception
        if not user.is_active:
            raise user_inactive_exception

        matching_token.revoked_at = datetime.now(tz=UTC)
        await self.repository.commit()

        access_token = create_access_token(TokenData(sub=str(user.id)))
        new_refresh_token_raw = generate_refresh_token()
        new_refresh_token_hashed = hash_refresh_token(new_refresh_token_raw)
        new_csrf_token = secrets.token_urlsafe(24)

        await self.repository.create_refresh_token(
            user_id=user.id,
            token_hash=new_refresh_token_hashed,
            expires_at=get_refresh_token_expiration(),
        )

        set_auth_cookies(response, new_refresh_token_raw, new_csrf_token)

        return Token(
            access_token=access_token,
            expires_in=int(auth_config.access_token_expire.total_seconds()),
            csrf_token=new_csrf_token,
        )

    async def logout(
        self,
        request: Request,
        response: Response,
        x_csrf_token: str | None,
    ) -> None:
        """Revoke the current refresh token and clear auth cookies.

        Args:
            request: Request used to read auth cookies.
            response: Response used to clear cookies.
            x_csrf_token: CSRF token header value.

        """
        refresh_token_raw = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")

        if (
            not refresh_token_raw
            or not csrf_token
            or not x_csrf_token
            or csrf_token != x_csrf_token
        ):
            clear_auth_cookies(response)
            return

        active_tokens = await self.repository.get_active_refresh_tokens()
        for token_record in active_tokens:
            if verify_refresh_token(refresh_token_raw, token_record.token_hash):
                token_record.revoked_at = datetime.now(tz=UTC)
                await self.repository.commit()
                break

        clear_auth_cookies(response)
