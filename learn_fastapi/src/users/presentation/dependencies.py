from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.service import UsersService


def get_users_service(session: AsyncSessionDep) -> UsersService:
    """Build a ``UsersService`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``UsersService`` instance.

    """
    return UsersService(session)


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]
