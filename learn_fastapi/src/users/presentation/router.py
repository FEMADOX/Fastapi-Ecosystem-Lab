from uuid import UUID

from fastapi import APIRouter
from fastapi_versionizer.versionizer import api_version
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.presentation.dependencies import UsersServiceDep
from learn_fastapi.src.users.schema import DeleteAccount, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@api_version(1)
@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    """Return the currently authenticated user's profile.

    Returns:
        The current authenticated user.

    """
    return UserResponse(**current_user.__dict__)


@api_version(1)
@router.get("/{user_id}")
async def get_account(
    user_id: UUID,
    service: UsersServiceDep,
    current_user: CurrentUserDep,
) -> UserResponse:
    """Return account details for the given user id.

    Returns:
        The requested user account.

    """
    return await service.get_account(user_id, current_user)


@api_version(1)
@router.patch("/{user_id}", response_model=UserResponse, status_code=HTTP_200_OK)
async def update_account(
    user_id: UUID,
    service: UsersServiceDep,
    current_user: CurrentUserDep,
    data: UserUpdate,
) -> User:
    """Update email and/or password for the target account.

    Returns:
        The updated user account.

    """
    return await service.update_account(user_id, current_user, data)


@api_version(1)
@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_account(
    user_id: UUID,
    service: UsersServiceDep,
    current_user: CurrentUserDep,
    data: DeleteAccount,
    response: Response,
) -> None:
    """Delete the target account after password confirmation."""
    await service.delete_account(user_id, current_user, data, response)
