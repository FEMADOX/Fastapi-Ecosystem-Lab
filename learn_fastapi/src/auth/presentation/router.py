from typing import Annotated

from fastapi import APIRouter, Header
from fastapi_versionizer.versionizer import api_version
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED

from learn_fastapi.src.auth.annotations import X_CSRF_TOKEN
from learn_fastapi.src.auth.schema import Token, TokenV2
from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.users.schema import UserCreate, UserResponse

from .dependencies import (
    AuthServiceDep,
    AuthServiceV2Dep,
    OAuth2PRFDep,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@api_version(1)
@router.post("/register", status_code=HTTP_201_CREATED)
async def register(service: AuthServiceDep, user_data: UserCreate) -> UserResponse:
    """Register a new user account.

    Args:
        service: Injected AuthService dependency.
        user_data: The user registration data (email and password).

    Returns:
        The newly created User ORM instance.

    """
    return await service.register(user_data)


@api_version(1)
@router.post("/token")
async def login(
    service: AuthServiceDep,
    form_data: OAuth2PRFDep,
    response: Response,
) -> Token:
    """Authenticate a user and return a JWT access token.

    Args:
        service: Injected AuthService dependency.
        form_data: The OAuth2 password request form data (username and password).
        response: The FastAPI Response object to set cookies on.

    Returns:
        Token: Returns the JWT access token.

    """
    return await service.login(form_data, response)


@api_version(2)
@router.post("/token")
async def login(  # noqa: F811
    service: AuthServiceV2Dep,
    form_data: OAuth2PRFDep,
    response: Response,
) -> TokenV2:
    """Authenticate a user and return a TokenV2.

    Args:
        service: Injected AuthServiceV2 dependency.
        form_data: The OAuth2 password request form data (username and password).
        response: The FastAPI Response object to set cookies on.

    Returns:
        TokenV2: Returns a new TokenV2 instance.
        - access_token: JWT access token
        - access_expires_in: Expiration timestamp of access token
        - access_token_type: Token type of access token
        - refresh_token: JWT refresh token
        - refresh_expires_in: Expiration timestamp of refresh token
        - csrf_token: CSRF token


    """
    return await service.login(form_data, response)


@api_version(1)
@router.post("/refresh")
async def refresh_token(
    service: AuthServiceDep,
    request: Request,
    x_csrf_token: X_CSRF_TOKEN,
) -> Token:
    """Refresh the JWT access token using a valid refresh token.

    Args:
        service: Injected AuthService dependency.
        request: The FastAPI Request object to read cookies from.
        x_csrf_token: The CSRF token from the X-CSRF-Token header.

    Returns:
        Token: A new access token and CSRF token if the refresh is successful.

    """
    return await service.refresh_token(request, x_csrf_token)


@api_version(1)
@router.post("/logout", status_code=204)
async def logout(
    service: AuthServiceDep,
    current_user: CurrentUserDep,
    request: Request,
    response: Response,
    x_csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> None:
    """Logout the user by revoking the refresh token and clearing cookies.

    Args:
        service: Injected AuthService dependency.
        current_user: The current authenticated user.
        request: The FastAPI Request object to read cookies from.
        response: The FastAPI Response object to clear cookies on.
        x_csrf_token: The CSRF token from the X-CSRF-Token header.

    """
    await service.logout(current_user, request, response, x_csrf_token)
