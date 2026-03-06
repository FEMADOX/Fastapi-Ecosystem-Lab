from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.future import select

from learn_fastapi.src.auth.annotations import OAuth2_Dep
from learn_fastapi.src.auth.models import User
from learn_fastapi.src.auth.schema import Token, UserCreate, UserResponse
from learn_fastapi.src.auth.utils import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from learn_fastapi.src.database import AsyncSessionDep

router = APIRouter(tags=["auth"])


async def get_current_user(token: OAuth2_Dep, session: AsyncSessionDep) -> User:
    """Get the current authenticated user from a JWT token.

    Returns:
        The authenticated User ORM instance.

    Raises:
        HTTPException: 401 if the token is invalid or the user does not exist.
        HTTPException: 400 if the user account is inactive.

    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if not email:
        raise credentials_exception

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, session: AsyncSessionDep) -> User:
    """Register a new user account.

    Returns:
        The newly created User ORM instance.

    Raises:
        HTTPException: 400 if the email address is already registered.

    """
    result = await session.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

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
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    """Authenticate a user and return a JWT access token.

    Returns:
        A dict containing the access token, token type, and user info.

    Raises:
        HTTPException: 401 if the credentials are incorrect.
        HTTPException: 400 if the user account is inactive.

    """
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive",
        )

    access_token = create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """Return the currently authenticated user's profile.

    Returns:
        The current User ORM instance.

    """
    return current_user
