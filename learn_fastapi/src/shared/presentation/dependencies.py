import uuid
from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.auth.infrastructure.jwt_access_token_verifier import (
    verify_access_token,
)
from learn_fastapi.src.auth.presentation.dependencies import OAuth2Dep
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.shared.application.dto import AuthenticatedAccount
from learn_fastapi.src.shared.presentation.exceptions import (
    invalid_expire_token_exception,
    user_doesnt_exist_exception,
    user_inactive_exception,
)
from learn_fastapi.src.users.domain.value_objects import PasswordHash
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository


async def get_current_user(
    session: AsyncSessionDep, token: OAuth2Dep
) -> AuthenticatedAccount:
    """Get the current authenticated user from a JWT token.

    Args:
        session: The database session dependency.
        token: The JWT access token from the Authorization header.

    Returns:
        The authenticated account.

    Raises:
        invalid_expire_token_exception: If the token is invalid or expired.
        user_inactive_exception: If the user account is inactive.
        user_doesnt_exist_exception: If the user does not exist.

    """
    user_id = verify_access_token(token)
    if not user_id:
        raise invalid_expire_token_exception()

    try:
        user_id_uuid = uuid.UUID(str(user_id.sub))
    except (TypeError, ValueError) as exception:
        raise invalid_expire_token_exception() from exception

    repository = SQLAlchemyUsersRepository(session)
    user = await repository.get_user_by_id(user_id_uuid)
    if not user:
        raise user_doesnt_exist_exception()
    if not user.is_active:
        raise user_inactive_exception()

    return AuthenticatedAccount(
        id=user.id,
        email=user.email,
        password_hash=PasswordHash(user.password_hash),
        is_active=user.is_active,
        is_superuser=user.is_superuser,
    )


CurrentUserDep = Annotated[AuthenticatedAccount, Depends(get_current_user)]
