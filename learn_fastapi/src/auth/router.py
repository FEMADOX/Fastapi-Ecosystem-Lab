import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Header
from sqlalchemy.future import select
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import (
    HTTP_201_CREATED,
)

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.utils.dependencies import CurrentUserDep

from .annotations import X_CSRF_TOKEN
from .config import auth_config
from .dependencies import OAuth2PRFDep
from .exceptions import (
    credentials_exception,
    email_already_registered_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)
from .models import RefreshToken, User
from .schema import Token, TokenData, UserCreate, UserResponse
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

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=HTTP_201_CREATED)
async def register(session: AsyncSessionDep, user_data: UserCreate) -> User:
    """Register a new user account.

    Args:
        session: The database session dependency.
        user_data: The user registration data (email and password).

    Returns:
        The newly created User ORM instance.

    Raises:
        email_already_registered_exception: If the email is already registered.

    """
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise email_already_registered_exception

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.post("/token", response_model=Token)
async def login(
    session: AsyncSessionDep,
    form_data: OAuth2PRFDep,
    response: Response,
) -> Token:
    """Authenticate a user and return a JWT access token.

    Args:
        session: The database session dependency.
        form_data: The OAuth2 password request form data (username and password).
        response: The FastAPI Response object to set cookies on.

    Returns:
        A dict containing the access token, token type, and user info.

    Raises:
        credentials_exception: If the credentials are incorrect.
        user_inactive_exception: If the user account is inactive.

    """
    result = await session.execute(
        select(User).where(User.email == form_data.username.lower())
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise credentials_exception

    if not user.is_active:
        raise user_inactive_exception

    access_token = create_access_token(TokenData(sub=str(user.id)))

    refresh_token_raw = generate_refresh_token()
    refresh_token_hashed = hash_password(refresh_token_raw)

    new_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hashed,
        expires_at=get_refresh_token_expiration(),
    )
    session.add(new_refresh_token)
    await session.commit()

    csrf_token = secrets.token_urlsafe(24)
    set_auth_cookies(response, refresh_token_raw, csrf_token)

    return Token(
        access_token=access_token,
        expires_in=int(auth_config.access_token_expire.total_seconds()),
        csrf_token=csrf_token,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    session: AsyncSessionDep,
    request: Request,
    response: Response,
    x_csrf_token: X_CSRF_TOKEN,
) -> Token:
    """Refresh the JWT access token using a valid refresh token.

    Args:
        session: The database session dependency.
        request: The FastAPI Request object to read cookies from.
        response: The FastAPI Response object to set new cookies on.
        x_csrf_token: The CSRF token from the X-CSRF-Token header.

    Returns:
        Token: A new access token and CSRF token if the refresh is successful.

    Raises:
        invalid_refresh_or_csrf_token_exception:
            If the refresh token or CSRF token is missing or invalid.
        invalid_refresh_token_exception: If the refresh token is invalid.
        user_doesnt_exist_exception:
            If the user associated with the refresh token does not exist.
        user_inactive_exception: If user is inactive.

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

    result = await session.execute(
        select(RefreshToken)
        .where(RefreshToken.revoked_at.is_(None))
        .where(RefreshToken.expires_at > datetime.now(tz=UTC))
    )
    valid_tokens = result.scalars().all()

    matching_token: RefreshToken | None = None
    for token_record in valid_tokens:
        if verify_refresh_token(refresh_token_raw, token_record.token_hash):
            matching_token = token_record
            break

    if not matching_token:
        raise invalid_refresh_token_exception

    # 3. User asociated
    user_result = await session.execute(
        select(User).where(User.id == matching_token.user_id)
    )
    user = user_result.scalar_one_or_none()

    if not user:
        raise user_doesnt_exist_exception
    if not user.is_active:
        raise user_inactive_exception

    # 4. Revoke old refresh token (rotation)
    matching_token.revoked_at = datetime.now(tz=UTC)

    # 5. Create new access token
    access_token = create_access_token(TokenData(sub=str(user.id)))
    new_refresh_token_raw = generate_refresh_token()
    new_refresh_token_hashed = hash_refresh_token(new_refresh_token_raw)
    new_csrf_token = secrets.token_urlsafe(24)

    session.add(
        RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_token_hashed,
            expires_at=get_refresh_token_expiration(),
        )
    )
    await session.commit()

    set_auth_cookies(response, new_refresh_token_raw, new_csrf_token)

    return Token(
        access_token=access_token,
        expires_in=int(auth_config.access_token_expire.total_seconds()),
        csrf_token=new_csrf_token,
    )


@router.post("/logout", status_code=204)
async def logout(
    session: AsyncSessionDep,
    request: Request,
    response: Response,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    """Logout the user by revoking the refresh token and clearing cookies.

    Args:
        session: The database session dependency.
        request: The FastAPI Request object to read cookies from.
        response: The FastAPI Response object to clear cookies on.
        x_csrf_token: The CSRF token from the X-CSRF-Token header.

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

    result = await session.execute(
        select(RefreshToken).where(RefreshToken.revoked_at.is_(None))
    )
    active_token = result.scalars().all()

    for token_record in active_token:
        if verify_refresh_token(refresh_token_raw, token_record.token_hash):
            token_record.revoked_at = datetime.now(tz=UTC)
            await session.commit()
            break

    clear_auth_cookies(response)


# @router.post("/logout-all", status_code=204)
# async def logout_all_devices(
#     session: AsyncSessionDep,
#     current_user: CurrentUserDep,
#     response: Response,
# ) -> None:
#     """Revoke all refresh tokens for current user and clear browser cookies."""
#     result = await session.execute(
#         select(RefreshToken)
#         .where(RefreshToken.user_id == current_user.id)
#         .where(RefreshToken.revoked_at.is_(None))
#     )
#     active_tokens = result.scalars().all()
#
#     now = datetime.now(UTC)
#     for token in active_tokens:
#         token.revoked_at = now
#
#     await session.commit()
#     clear_auth_cookies(response)


@router.get("/me", response_model=UserResponse)
# async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
async def get_me(current_user: CurrentUserDep) -> User:
    """Return the currently authenticated user's profile.

    Args:
        current_user: The current authenticated user, injected by the dependency.

    Returns:
        The current User ORM instance.

    """
    return current_user
