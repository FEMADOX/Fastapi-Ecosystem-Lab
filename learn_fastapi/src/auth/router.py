import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from starlette.status import (
    HTTP_201_CREATED,
)

from learn_fastapi.src.auth.exceptions import (
    credentials_exception,
    email_already_registered_exception,
    invalid_expire_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)
from learn_fastapi.src.database import AsyncSessionDep

from .annotations import OAuth2_Dep, OAuth2PRFDep
from .models import User
from .schema import Token, TokenData, UserCreate, UserResponse
from .utils import (
    create_access_token,
    hash_password,
    verify_access_token,
    verify_password,
)

router = APIRouter()


async def get_current_user(session: AsyncSessionDep, token: OAuth2_Dep) -> User:
    """Get the current authenticated user from a JWT token.

    Args:
        session: The database session dependency.
        token: The JWT access token from the Authorization header.

    Returns:
        The authenticated User ORM instance.

    Raises:
        invalid_expire_token_exception: If the token is invalid or expired.
        user_inactive_exception: If the user account is inactive.
        user_doesnt_exist_exception: If the user does not exist.

    """
    # payload = decode_access_token(token)
    user_id = verify_access_token(token)
    if not user_id:
        raise invalid_expire_token_exception

    try:
        user_id_uuid = uuid.UUID(str(user_id.sub))
    except (TypeError, ValueError) as exception:
        raise invalid_expire_token_exception from exception

    result = await session.execute(select(User).where(User.id == user_id_uuid))
    user = result.scalar_one_or_none()
    if not user:
        raise user_doesnt_exist_exception
    if not user.is_active:
        raise user_inactive_exception

    return user


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
async def login(session: AsyncSessionDep, form_data: OAuth2PRFDep) -> Token:
    """Authenticate a user and return a JWT access token.

    Args:
        session: The database session dependency.
        form_data: The OAuth2 password request form data (username and password).

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

    return Token(
        access_token=access_token,
        # token_type="bearer",
    )


# TODO (FENYXZ): Add endpoint to refresh access tokens using refresh tokens


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the currently authenticated user's profile.

    Args:
        current_user: The current authenticated user, injected by the dependency.

    Returns:
        The current User ORM instance.

    """
    return current_user
