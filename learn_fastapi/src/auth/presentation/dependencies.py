from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from learn_fastapi.src.auth.application.use_cases import (
    CreateRefreshTokenUseCase,
    FullLoginUseCase,
    GetRefreshTokenUseCase,
    IssueAccessTokenUseCase,
    LoginUseCase,
    LogoutUseCase,
    RefreshAccessTokenUseCase,
    RegisterAccountUseCase,
    RevokeRefreshTokensUseCase,
    RevokeRefreshTokenUseCase,
)
from learn_fastapi.src.auth.config import auth_config
from learn_fastapi.src.auth.infrastructure.argon2_refresh_token_hasher import (
    Argon2RefreshTokenHasher,
)
from learn_fastapi.src.auth.infrastructure.events import SSEAuthEventPublisher
from learn_fastapi.src.auth.infrastructure.jwt_access_token_issuer import (
    PyJWTAccessTokenIssuer,
)
from learn_fastapi.src.auth.infrastructure.repository import SQLAlchemyAuthRepository
from learn_fastapi.src.auth.infrastructure.secrets_refresh_token_generator import (
    SecretsRefreshTokenGenerator,
)
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.shared.infrastructure.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from learn_fastapi.src.shared.infrastructure.system_clock import SystemClock
from learn_fastapi.src.users.application.use_cases import (
    GetUserByRefreshTokenUseCase,
    RegisterUserUseCase,
)
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


def _issue_access_token_uc() -> IssueAccessTokenUseCase:
    return IssueAccessTokenUseCase(
        PyJWTAccessTokenIssuer(
            auth_config.secret_key.get_secret_value(),
            auth_config.algorithm,
        ),
        SystemClock(),
        auth_config.access_token_expire,
    )


def get_full_login_use_case(session: AsyncSessionDep) -> FullLoginUseCase:
    auth_repo = SQLAlchemyAuthRepository(session)
    users_repo = SQLAlchemyUsersRepository(session)

    return FullLoginUseCase(
        login=LoginUseCase(users_repo, Argon2PasswordHasher()),
        issue_access_token=_issue_access_token_uc(),
        get_refresh_token=GetRefreshTokenUseCase(auth_repo),
        revoke_refresh_tokens=RevokeRefreshTokensUseCase(auth_repo),
        create_refresh_token=CreateRefreshTokenUseCase(
            auth_repo,
            SecretsRefreshTokenGenerator(),
            Argon2RefreshTokenHasher(),
            SystemClock(),
            auth_config.refresh_token_expire,
        ),
        event_publisher=SSEAuthEventPublisher(),
    )


def get_refresh_access_token_use_case(
    session: AsyncSessionDep,
) -> RefreshAccessTokenUseCase:
    return RefreshAccessTokenUseCase(
        get_user_by_refresh_token=GetUserByRefreshTokenUseCase(
            SQLAlchemyUsersRepository(session)
        ),
        issue_access_token=_issue_access_token_uc(),
    )


def get_logout_use_case(session: AsyncSessionDep) -> LogoutUseCase:
    auth_repo = SQLAlchemyAuthRepository(session)

    return LogoutUseCase(
        get_refresh_token=GetRefreshTokenUseCase(auth_repo),
        revoke_refresh_token=RevokeRefreshTokenUseCase(auth_repo),
        event_publisher=SSEAuthEventPublisher(),
    )


def get_register_account_use_case(
    session: AsyncSessionDep,
) -> RegisterAccountUseCase:
    return RegisterAccountUseCase(
        register_user=RegisterUserUseCase(
            # RegisterUserUseCase receives PasswordHasher in the later users
            # migration; this branch keeps its current one-argument contract.
            SQLAlchemyUsersRepository(session)
        ),
        event_publisher=SSEAuthEventPublisher(),
    )


OAuth2PRFDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OAuth2Dep = Annotated[str, Depends(oauth2_scheme)]

FullLoginUseCaseDep = Annotated[FullLoginUseCase, Depends(get_full_login_use_case)]
RefreshAccessTokenUseCaseDep = Annotated[
    RefreshAccessTokenUseCase, Depends(get_refresh_access_token_use_case)
]
LogoutUseCaseDep = Annotated[LogoutUseCase, Depends(get_logout_use_case)]
RegisterAccountUseCaseDep = Annotated[
    RegisterAccountUseCase, Depends(get_register_account_use_case)
]
