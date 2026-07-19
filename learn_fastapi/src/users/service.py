from dataclasses import dataclass
from uuid import UUID

from starlette.responses import Response

from learn_fastapi.src.auth.utils import (
    clear_auth_cookies,
    verify_password,
)
from learn_fastapi.src.shared.presentation.exceptions import (
    user_doesnt_exist_exception,
)
from learn_fastapi.src.users.application.commands import UpdateUserCommand
from learn_fastapi.src.users.application.queries import GetUserByIdQuery
from learn_fastapi.src.users.application.use_cases import (
    DeleteUserUseCase,
    GetUserByIdUseCase,
    UpdateUserUseCase,
)
from learn_fastapi.src.users.domain.errors import UserDoesntExistError
from learn_fastapi.src.users.infrastructure.mappers import persisted_user_to_schema
from learn_fastapi.src.users.presentation.exceptions import (
    incorrect_password_exception,
    only_user_owner_is_authorized,
)
from learn_fastapi.src.utils.service import BaseService

from .models import User as UserModel
from .schema import DeleteAccount, UserResponse, UserUpdate


@dataclass(frozen=True, slots=True)
class UsersUseCases:
    """Application use cases required by ``UsersService``."""

    get_user_by_id: GetUserByIdUseCase
    update_user: UpdateUserUseCase
    delete_user: DeleteUserUseCase


class UsersService(BaseService):
    """Service class for user account business logic."""

    def __init__(self, use_cases: UsersUseCases) -> None:
        """Initialize the service with an async database session."""
        self.use_cases = use_cases

    async def verify_userid_and_auth_user(
        self,
        user_id: UUID,
        authorized_user: UserModel,
        user_password: str | None,
    ) -> UserResponse:
        """Verify if the authorized user is the owner.

        This method verify if the authorized user is the owner of the user_id account
        if isn't the case this method will raise the corresponding exception.

        Admin users will be ignored by this verification method.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            user_password: The user current password

        Returns:
            User: The user instance matching the user_id
                if the authorized_user is the owner or
                an admin user, otherwise ``None``.

        Raises:
            user_doesnt_exist_exception: If the user does not exist.
            only_user_owner_is_authorized: If the authorized user is not the owner
                of the account
            incorrect_password_exception: If `current_password` is wrong.

        """
        try:
            user_from_user_id = await self.use_cases.get_user_by_id.execute(
                GetUserByIdQuery(user_id)
            )
            schema = persisted_user_to_schema(user_from_user_id)
        except UserDoesntExistError as exc:
            raise user_doesnt_exist_exception() from exc

        if authorized_user.is_superuser:
            return schema

        if not user_from_user_id.has_same_identity_as(authorized_user.id):
            raise only_user_owner_is_authorized()

        if user_password and not verify_password(
            user_password, authorized_user.password_hash
        ):
            raise incorrect_password_exception()

        return schema

    async def get_account(
        self, user_id: UUID, authorized_user: UserModel
    ) -> UserResponse:
        """Return account details for an allowed user.

        Args:
            user_id: The user id of the user you want to retrieve.
            authorized_user: The currently authenticated user instance.

        Returns:
            The requested user when access is allowed.

        """
        return await self.verify_userid_and_auth_user(user_id, authorized_user, None)

    async def update_account(
        self, user_id: UUID, authorized_user: UserModel, data: UserUpdate
    ) -> UserResponse:
        """Update the authenticated user's email and/or password.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The update payload containing the current password
                and optional new email / new password.

        Returns:
            The refreshed user instance after the update.

        """
        await self.verify_userid_and_auth_user(
            user_id, authorized_user, data.current_password
        )

        updated_user, changed_fields = await self.use_cases.update_user.execute(
            UpdateUserCommand(authorized_user.id, data.new_email, data.new_password)
        )

        await self._broadcast_sse_event(
            "user.account_updated",
            {"user_id": str(updated_user.id), "changed_fields": changed_fields},
            user_id=updated_user.id,
        )

        return persisted_user_to_schema(updated_user)

    async def delete_account(
        self,
        user_id: UUID,
        authorized_user: UserModel,
        data: DeleteAccount,
        response: Response,
    ) -> None:
        """Permanently delete the authenticated user's account.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The deletion confirmation payload containing the user's password.
            response: Response used to clear auth cookies after deletion.

        Raises:
            user_doesnt_exist_exception: If the user does not exist.

        """
        await self.verify_userid_and_auth_user(user_id, authorized_user, data.password)

        try:
            await self.use_cases.delete_user.execute(authorized_user.id)
        except UserDoesntExistError as exc:
            raise user_doesnt_exist_exception() from exc

        await self._broadcast_sse_event(
            "user.account_deleted",
            {"user_id": str(authorized_user.id)},
            user_id=authorized_user.id,
        )

        clear_auth_cookies(response)
