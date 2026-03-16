from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)

from learn_fastapi.src.utils.dependencies import CurrentUserDep

from .annotations import X_CSRF_TOKEN
from .dependencies import AuthServiceDep, OAuth2PRFDep
from .models import User
from .schema import DeleteAccount, Token, UserCreate, UserResponse, UserUpdate

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
        A dict containing the access token, token type, and user info.

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


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: CurrentUserDep) -> User:
    """Return the currently authenticated user's profile.

    Args:
        current_user: The current authenticated user, injected by the dependency.

    Returns:
        The current User Response instance.

    """
    return current_user


@router.patch("/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
async def update_me(
    user_id: UUID,
    service: AuthServiceDep,
    current_user: CurrentUserDep,
    data: UserUpdate,
) -> User:
    """Update the authenticated user's email and/or password.

    Args:
        user_id: The user id of the user you want to update
        service: Injected AuthService dependency.
        current_user: The current authenticated user.
        data: The update payload
            (current password required*; new email/password optional*).

    Returns:
        The updated User Response instance.

    """
    return await service.update_account(user_id, current_user, data)


@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_me(
    user_id: UUID,
    service: AuthServiceDep,
    current_user: CurrentUserDep,
    data: DeleteAccount,
    response: Response,
) -> None:
    """Permanently delete the authenticated user's account.

    Args:
        user_id: The user id of the user you want to update
        service: Injected AuthService dependency.
        current_user: The current authenticated user.
        data: The deletion confirmation payload (current password required).
        response: The FastAPI Response object used to clear auth cookies.

    """
    await service.delete_account(user_id, current_user, data, response)
