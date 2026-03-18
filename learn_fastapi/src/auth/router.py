from typing import Annotated

from fastapi import APIRouter, Header
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_201_CREATED

from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.schema import UserCreate, UserResponse
from learn_fastapi.src.utils.dependencies import CurrentUserDep

from .annotations import X_CSRF_TOKEN
from .dependencies import AuthServiceDep, OAuth2PRFDep
from .schema import Token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=HTTP_201_CREATED)
async def register(service: AuthServiceDep, user_data: UserCreate) -> User:
    """Register a new user account.

    Args:
        service: Injected AuthService dependency.
        user_data: The user registration data (email and password).

    Returns:
        The newly created User ORM instance.

    """
    return await service.register(user_data)


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


@router.post("/refresh")
async def refresh_token(
    service: AuthServiceDep,
    current_user: CurrentUserDep,
    request: Request,
    response: Response,
    x_csrf_token: X_CSRF_TOKEN,
) -> Token:
    """Refresh the JWT access token using a valid refresh token.

    Args:
        service: Injected AuthService dependency.
        current_user: The current authenticated user.
        request: The FastAPI Request object to read cookies from.
        response: The FastAPI Response object to set new cookies on.
        x_csrf_token: The CSRF token from the X-CSRF-Token header.

    Returns:
        Token: A new access token and CSRF token if the refresh is successful.

    """
    return await service.refresh_token(current_user, request, response, x_csrf_token)


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
