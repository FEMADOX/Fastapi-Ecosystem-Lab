from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.application.use_cases import (
    DeleteUserUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
)
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository
from learn_fastapi.src.users.service import UsersService, UsersUseCases


def get_users_service(session: AsyncSessionDep) -> UsersService:
    """Build a ``UsersService`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``UsersService`` instance.

    """
    clean_user_repository = SQLAlchemyUsersRepository(session)

    return UsersService(
        UsersUseCases(
            GetUserByIdUseCase(clean_user_repository),
            UpdateUserUseCase(clean_user_repository),
            DeleteUserUseCase(clean_user_repository),
        )
    )


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]
