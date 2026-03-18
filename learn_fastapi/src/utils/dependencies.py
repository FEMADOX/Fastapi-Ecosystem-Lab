import uuid
from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.auth.dependencies import OAuth2_Dep
from learn_fastapi.src.auth.repository import AuthRepository
from learn_fastapi.src.auth.utils import verify_access_token
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.models import User

from .exceptions import (
    invalid_expire_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)


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
    user_id = verify_access_token(token)
    if not user_id:
        raise invalid_expire_token_exception

    try:
        user_id_uuid = uuid.UUID(str(user_id.sub))
    except (TypeError, ValueError) as exception:
        raise invalid_expire_token_exception from exception

    repository = AuthRepository(session)
    user = await repository.get_user_by_id(user_id_uuid)
    if not user:
        raise user_doesnt_exist_exception
    if not user.is_active:
        raise user_inactive_exception

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
