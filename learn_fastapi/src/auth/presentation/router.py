import secrets
from typing import Annotated

from fastapi import APIRouter, Header
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED

from learn_fastapi.src.auth.application.commands import LoginCommand
from learn_fastapi.src.auth.application.queries import GetUserByRefreshTokenQuery
from learn_fastapi.src.auth.domain.errors import (
    CredentialsError,
    DoesntExistUserError,
)
from learn_fastapi.src.auth.presentation.cookies import (
    clear_auth_cookies,
    set_auth_cookies,
)
from learn_fastapi.src.auth.presentation.exceptions import (
    credentials_exception,
    invalid_refresh_or_csrf_token_exception,
    invalid_refresh_token_exception,
)
from learn_fastapi.src.auth.presentation.schemas import Token, TokenV2
from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.shared.presentation.exceptions import (
    email_already_registered_exception,
    user_inactive_exception,
)
from learn_fastapi.src.users.application.commands import RegisterNewUserCommand
from learn_fastapi.src.users.domain.errors import (
    UserAlreadyExistsError,
    UserInactiveError,
)
from learn_fastapi.src.users.schema import UserCreate, UserResponse

from .dependencies import (
    FullLoginUseCaseDep,
    LogoutUseCaseDep,
    OAuth2PRFDep,
    RefreshAccessTokenUseCaseDep,
    RegisterAccountUseCaseDep,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@api_version(1)
@router.post("/register", status_code=HTTP_201_CREATED)
async def register(
    use_case: RegisterAccountUseCaseDep, user_data: UserCreate
) -> UserResponse:
    try:
        new_user = await use_case.execute(
            RegisterNewUserCommand(user_data.email, user_data.password)
        )
    except UserAlreadyExistsError as exc:
        raise email_already_registered_exception() from exc

    # Users presentation has not moved yet, so map the cross-app result here.
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        is_active=new_user.is_active,
        is_superuser=new_user.is_superuser,
    )


@api_version(1)
@router.post("/token")
async def login(
    use_case: FullLoginUseCaseDep,
    form_data: OAuth2PRFDep,
    response: Response,
) -> Token:
    try:
        result = await use_case.execute(
            LoginCommand(email=form_data.username.lower(), password=form_data.password)
        )
    except (DoesntExistUserError, CredentialsError) as exc:
        raise credentials_exception() from exc
    except UserInactiveError as exc:
        raise user_inactive_exception() from exc

    csrf_token = secrets.token_urlsafe(24)
    set_auth_cookies(response, result.refresh_token_raw, csrf_token)

    return Token(
        access_token=result.access_token,
        expires_in=result.access_expires_in,
        csrf_token=csrf_token,
    )


@api_version(2)
@router.post("/token")
async def login(  # noqa: F811
    use_case: FullLoginUseCaseDep,
    form_data: OAuth2PRFDep,
    response: Response,
) -> TokenV2:
    try:
        result = await use_case.execute(
            LoginCommand(email=form_data.username.lower(), password=form_data.password)
        )
    except (DoesntExistUserError, CredentialsError) as exc:
        raise credentials_exception() from exc
    except UserInactiveError as exc:
        raise user_inactive_exception() from exc

    csrf_token = secrets.token_urlsafe(24)
    set_auth_cookies(response, result.refresh_token_raw, csrf_token)

    return TokenV2(
        access_token=result.access_token,
        access_expires_in=result.access_expires_in,
        refresh_token=result.refresh_token_raw,
        refresh_expires_in=result.refresh_expires_in,
        csrf_token=csrf_token,
    )


@api_version(1)
@router.post("/refresh")
async def refresh_token(
    use_case: RefreshAccessTokenUseCaseDep,
    request: Request,
    x_csrf_token: Annotated[str, Header(alias="X-CSRF-Token")],
) -> Token:
    refresh_token_raw = request.cookies.get("refresh_token")
    csrf_token = request.cookies.get("csrf_token")

    if (
        not refresh_token_raw
        or not csrf_token
        or not x_csrf_token
        or x_csrf_token != csrf_token
    ):
        raise invalid_refresh_or_csrf_token_exception()

    try:
        access_token = await use_case.execute(
            GetUserByRefreshTokenQuery(refresh_token_raw)
        )
    except DoesntExistUserError as exc:
        raise invalid_refresh_token_exception() from exc

    return Token(
        access_token=access_token.value,
        expires_in=access_token.expires_in,
        csrf_token=csrf_token,
    )


@api_version(1)
@router.post("/logout", status_code=204)
async def logout(
    use_case: LogoutUseCaseDep,
    current_user: CurrentUserDep,
    request: Request,
    response: Response,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    refresh_token_raw = request.cookies.get("refresh_token")
    csrf_token = request.cookies.get("csrf_token")

    has_valid_csrf = (
        refresh_token_raw and csrf_token and x_csrf_token and csrf_token == x_csrf_token
    )
    await use_case.execute(
        current_user.id,
        refresh_token_raw if has_valid_csrf else None,
    )

    clear_auth_cookies(response)
