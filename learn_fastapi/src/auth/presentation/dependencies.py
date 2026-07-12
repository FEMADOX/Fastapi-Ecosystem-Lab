from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from learn_fastapi.src.auth.application.use_cases import (
    CreateRefreshTokenUseCase,
    GetRefreshTokenUseCase,
    LoginUseCase,
    RevokeRefreshTokensUseCase,
    RevokeRefreshTokenUseCase,
)
from learn_fastapi.src.auth.infrastructure.repository import SQLAlchemyAuthRepository
from learn_fastapi.src.auth.service import AuthService, AuthServiceV2
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.users.application.use_cases import (
    GetUserByEmailUseCase,
    GetUserByRefreshTokenUseCase,
    RegisterUserUseCase,
)
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


def get_auth_service(session: AsyncSessionDep) -> AuthService:
    """Build an ``AuthService`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``AuthService`` instance.

    """
    clean_auth_repository = SQLAlchemyAuthRepository(session)
    clean_users_repository = SQLAlchemyUsersRepository(session)

    return AuthService(
        GetRefreshTokenUseCase(clean_auth_repository),
        GetUserByEmailUseCase(clean_users_repository),
        GetUserByRefreshTokenUseCase(clean_users_repository),
        LoginUseCase(clean_users_repository),
        RegisterUserUseCase(clean_users_repository),
        CreateRefreshTokenUseCase(clean_auth_repository),
        RevokeRefreshTokensUseCase(clean_auth_repository),
        RevokeRefreshTokenUseCase(clean_auth_repository),
    )


def get_auth_service_v2(service: AuthServiceDep) -> AuthServiceV2:
    """Build an ``AuthServiceV2`` for the current request.

    Args:
        service: Injected AuthService dependency.

    Returns:
        A configured ``AuthServiceV2`` instance.

    """
    return AuthServiceV2(
        service.get_refresh_token_use_case,
        service.get_user_by_email_use_case,
        service.get_user_by_refresh_token_use_case,
        service.login_use_case,
        service.register_user_use_case,
        service.create_refresh_token_use_case,
        service.revoke_refresh_tokens_use_case,
        service.revoke_refresh_token_use_case,
    )


OAuth2PRFDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OAuth2Dep = Annotated[str, Depends(oauth2_scheme)]

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AuthServiceV2Dep = Annotated[AuthServiceV2, Depends(get_auth_service_v2)]
