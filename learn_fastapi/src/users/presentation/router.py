from uuid import UUID

from fastapi import APIRouter
from fastapi_versionizer.versionizer import api_version
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from learn_fastapi.src.auth.presentation.cookies import clear_auth_cookies
from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.shared.presentation.exceptions import (
    email_already_registered_exception,
    user_doesnt_exist_exception,
)
from learn_fastapi.src.users.application.commands import (
    DeleteAccountCommand,
    UpdateUserCommand,
)
from learn_fastapi.src.users.application.queries import GetAccountQuery
from learn_fastapi.src.users.domain.errors import (
    IncorrectPasswordError,
    OnlyOwnerIsAuthorizedError,
    UserAlreadyExistsError,
    UserDoesntExistError,
)
from learn_fastapi.src.users.presentation.dependencies import (
    DeleteAccountUseCaseDep,
    GetAccountUseCaseDep,
    UpdateUserUseCaseDep,
)
from learn_fastapi.src.users.presentation.exceptions import (
    incorrect_password_exception,
    only_user_owner_is_authorized,
)
from learn_fastapi.src.users.presentation.mappers import persisted_user_to_schema
from learn_fastapi.src.users.presentation.schemas import (
    DeleteAccount,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@api_version(1)
@router.get("/me")
async def get_me(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )


@api_version(1)
@router.get("/{user_id}")
async def get_account(
    user_id: UUID,
    get_account_uc: GetAccountUseCaseDep,
    current_user: CurrentUserDep,
) -> UserResponse:
    try:
        user = await get_account_uc.execute(
            GetAccountQuery(user_id, current_user.to_actor())
        )
    except OnlyOwnerIsAuthorizedError as exc:
        raise only_user_owner_is_authorized() from exc
    except UserDoesntExistError as exc:
        raise user_doesnt_exist_exception() from exc

    return persisted_user_to_schema(user)


@api_version(1)
@router.patch("/{user_id}", status_code=HTTP_200_OK)
async def update_account(
    user_id: UUID,
    current_user: CurrentUserDep,
    data: UserUpdate,
    update_user: UpdateUserUseCaseDep,
) -> UserResponse:
    try:
        updated_user, _ = await update_user.execute(
            UpdateUserCommand(
                user_id,
                current_user,
                data.current_password,
                data.new_email,
                data.new_password,
            )
        )
    except OnlyOwnerIsAuthorizedError as exc:
        raise only_user_owner_is_authorized() from exc
    except IncorrectPasswordError as exc:
        raise incorrect_password_exception() from exc
    except UserAlreadyExistsError as exc:
        raise email_already_registered_exception() from exc
    except UserDoesntExistError as exc:
        raise user_doesnt_exist_exception() from exc

    return persisted_user_to_schema(updated_user)


@api_version(1)
@router.delete("/{user_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_account(
    user_id: UUID,
    current_user: CurrentUserDep,
    data: DeleteAccount,
    delete_account_uc: DeleteAccountUseCaseDep,
    response: Response,
) -> None:
    try:
        await delete_account_uc.execute(
            DeleteAccountCommand(user_id, current_user, data.password)
        )
    except OnlyOwnerIsAuthorizedError as exc:
        raise only_user_owner_is_authorized() from exc
    except IncorrectPasswordError as exc:
        raise incorrect_password_exception() from exc
    except UserDoesntExistError as exc:
        raise user_doesnt_exist_exception() from exc

    if current_user.id == user_id:
        clear_auth_cookies(response)
