import uuid
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from learn_fastapi.src.auth.dependencies import OAuth2_Dep
from learn_fastapi.src.auth.exceptions import (
    invalid_expire_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)
from learn_fastapi.src.auth.models import User
from learn_fastapi.src.auth.utils import verify_access_token
from learn_fastapi.src.database import AsyncSessionDep


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

    result = await session.execute(select(User).where(User.id == user_id_uuid))  # ty:ignore[invalid-argument-type]
    user = result.scalar_one_or_none()
    if not user:
        raise user_doesnt_exist_exception
    if not user.is_active:
        raise user_inactive_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
