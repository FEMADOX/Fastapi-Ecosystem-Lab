from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.shared.infrastructure.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from learn_fastapi.src.users.application.use_cases import (
    DeleteAccountUseCase,
    DeleteUserUseCase,
    GetAccountUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
)
from learn_fastapi.src.users.infrastructure.events import SSEUsersEventPublisher
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository


def get_account_use_case(session: AsyncSessionDep) -> GetAccountUseCase:
    return GetAccountUseCase(GetUserByIdUseCase(SQLAlchemyUsersRepository(session)))


def get_update_user_use_case(session: AsyncSessionDep) -> UpdateUserUseCase:
    password_hasher = Argon2PasswordHasher()
    return UpdateUserUseCase(
        SQLAlchemyUsersRepository(session),
        password_hasher,
        SSEUsersEventPublisher(),
    )


def get_delete_account_use_case(session: AsyncSessionDep) -> DeleteAccountUseCase:
    repo = SQLAlchemyUsersRepository(session)
    return DeleteAccountUseCase(
        get_user_by_id=GetUserByIdUseCase(repo),
        delete_user=DeleteUserUseCase(repo),
        event_publisher=SSEUsersEventPublisher(),
        password_hasher=Argon2PasswordHasher(),
    )


GetAccountUseCaseDep = Annotated[GetAccountUseCase, Depends(get_account_use_case)]
UpdateUserUseCaseDep = Annotated[UpdateUserUseCase, Depends(get_update_user_use_case)]
DeleteAccountUseCaseDep = Annotated[
    DeleteAccountUseCase, Depends(get_delete_account_use_case)
]
