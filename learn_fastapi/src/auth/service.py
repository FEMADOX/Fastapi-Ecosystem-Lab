import secrets
from datetime import UTC, datetime
from uuid import UUID

from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import Response

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.utils.exceptions import user_doesnt_exist_exception

from .config import auth_config
from .exceptions import (
    credentials_exception,
    email_already_registered_exception,
    incorrect_password_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
    only_user_owner_is_authorized,
    user_inactive_exception,
)
from .models import User
from .repository import AuthRepository
from .schema import DeleteAccount, Token, TokenData, UserCreate, UserUpdate
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

        user_id = user.id

        access_token = create_access_token(TokenData(sub=str(user_id)))
        refresh_token_raw = generate_refresh_token()
        refresh_token_hashed = hash_refresh_token(refresh_token_raw)

        user_refresh_token = await self.repository.get_refresh_token(user_id)
        if user_refresh_token:
            await self.repository.revoke_refresh_token(user_id)

        csrf_token = secrets.token_urlsafe(24)

        await self.repository.create_refresh_token(
            user_id=user_id,
            token_hash=refresh_token_hashed,
            expires_at=get_refresh_token_expiration(),
        )

        set_auth_cookies(response, refresh_token_raw, csrf_token)

        return Token(
            access_token=access_token,
            expires_in=int(auth_config.access_token_expire.total_seconds()),
            csrf_token=csrf_token,
        )

    async def refresh_token(
        self,
        user: User,
        request: Request,
        response: Response,
        x_csrf_token: str,
    ) -> Token:
        """Rotate refresh token and issue a new access token.

        Args:
            user: The current authenticated user.
            request: Request used to read cookies.
            response: Response used to write rotated cookies.
            x_csrf_token: CSRF token provided in the request header.

        Returns:
            A new token response.

        Raises:
            invalid_refresh_or_csrf_token_exception: If CSRF/cookie validation fails.
            invalid_refresh_token_exception: If the refresh token is invalid or expired.

        """
        refresh_token_raw = request.cookies.get("refresh_token")
        csrf_token = request.cookies.get("csrf_token")
        user_id = user.id

        if (
            not refresh_token_raw
            or not csrf_token
            or not x_csrf_token
            or x_csrf_token != csrf_token
        ):
            raise invalid_refresh_or_csrf_token_exception

        user_refresh_token = await self.repository.get_refresh_token(user_id)

        if not user_refresh_token or not verify_refresh_token(
            refresh_token_raw, user_refresh_token.token_hash
        ):
            raise invalid_refresh_token_exception

        await self.repository.revoke_refresh_token(user_id)

        access_token = create_access_token(TokenData(sub=str(user_id)))
        new_refresh_token_raw = generate_refresh_token()
        new_refresh_token_hashed = hash_refresh_token(new_refresh_token_raw)
        new_csrf_token = secrets.token_urlsafe(24)

        await self.repository.create_refresh_token(
            user_id=user_id,
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
            not refresh_token_raw
            or not csrf_token
            or not x_csrf_token
            or csrf_token != x_csrf_token
        ):
            clear_auth_cookies(response)
            return

        token_record = await self.repository.get_refresh_token(user.id)
        if not token_record:
            clear_auth_cookies(response)
            return
        if verify_refresh_token(refresh_token_raw, token_record.token_hash):
            token_record.revoked_at = datetime.now(tz=UTC)
            await self.repository.commit()

        clear_auth_cookies(response)

    async def verify_userid_and_auth_user(
        self,
        user_id: UUID,
        authorized_user: User,
        user_password: str,
    ) -> None:
        """Verify if the authorized user is the owner.

        This method verify if the authorized user is the owner of the user_id account
        if isn't the case this method will raise the corresponding exception.

        Admin users will be ignore by this verification method.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            user_password: The user current password

        Raises:
            user_doesnt_exist_exception: If the user does not exist.
            only_user_owner_is_authorized: If the authorized user is not the owner
                of the accont
            incorrect_password_exception: If `current_password` is wrong.

        """
        user_from_user_id = await self.repository.get_user_by_id(user_id)
        if not user_from_user_id:
            raise user_doesnt_exist_exception

        if authorized_user.is_superuser:
            return

        if not user_from_user_id == authorized_user:
            raise only_user_owner_is_authorized

        if not verify_password(user_password, authorized_user.password_hash):
            raise incorrect_password_exception

    async def update_account(
        self, user_id: UUID, authorized_user: User, data: UserUpdate
    ) -> User:
        """Update the authenticated user's email and/or password.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The update payload containing the current password
                and optional new email / new password.

        Returns:
            The refreshed user instance after the update.

        Raises:
            email_already_registered_exception: If ``new_email`` is already taken.

        """
        await self.verify_userid_and_auth_user(
            user_id, authorized_user, data.current_password
        )
        if data.new_email:
            existing = await self.repository.get_user_by_email(data.new_email)
            if existing:
                raise email_already_registered_exception
            authorized_user.email = data.new_email

        if data.new_password:
            authorized_user.password_hash = hash_password(data.new_password)

        return await self.repository.update_user(authorized_user)

    async def delete_account(
        self,
        user_id: UUID,
        authorized_user: User,
        data: DeleteAccount,
        response: Response,
    ) -> None:
        """Permanently delete the authenticated user's account.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The deletion confirmation payload containing the user's password.
            response: Response used to clear auth cookies after deletion.

        """
        await self.verify_userid_and_auth_user(user_id, authorized_user, data.password)
        await self.repository.delete_user(authorized_user)
        clear_auth_cookies(response)
