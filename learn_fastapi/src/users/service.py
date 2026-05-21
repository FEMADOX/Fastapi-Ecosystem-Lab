from uuid import UUID

from starlette.responses import Response

from learn_fastapi.src.auth.utils import (
    clear_auth_cookies,
    hash_password,
    verify_password,
)
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.utils.exceptions import (
    email_already_registered_exception,
    user_doesnt_exist_exception,
)
from learn_fastapi.src.utils.service import BaseService

from .exceptions import incorrect_password_exception, only_user_owner_is_authorized
from .models import User
from .repository import UsersRepository
from .schema import DeleteAccount, UserUpdate


class UsersService(BaseService):
    """Service class for user account business logic."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository: UsersRepository = UsersRepository(session)

    async def verify_userid_and_auth_user(
        self,
        user_id: UUID,
        authorized_user: User,
        user_password: str | None,
    ) -> User:
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
        user_from_user_id = await self.repository.get_user_by_id(user_id)
        if not user_from_user_id:
            raise user_doesnt_exist_exception()

        if authorized_user.is_superuser:
            return user_from_user_id

        if not user_from_user_id == authorized_user:
            raise only_user_owner_is_authorized()

        if user_password and not verify_password(
            user_password, authorized_user.password_hash
        ):
            raise incorrect_password_exception()

        return user_from_user_id

    async def get_account(self, user_id: UUID, authorized_user: User) -> User:
        """Return account details for an allowed user.

        Args:
            user_id: The user id of the user you want to retrieve.
            authorized_user: The currently authenticated user instance.

        Returns:
            The requested user when access is allowed.

        """
        return await self.verify_userid_and_auth_user(user_id, authorized_user, None)

    async def update_account(
        self, user_id: UUID, authorized_user: User, data: UserUpdate
    ) -> User:
        """Update the authenticated user's email and/or password.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The update payload containing the current password
                and optional new email / new password.

        Returns:
            The refreshed user instance after the update.

        Raises:
            email_already_registered_exception: If ``new_email`` is already taken.

        """
        await self.verify_userid_and_auth_user(
            user_id, authorized_user, data.current_password
        )

        changed_fields: list[str] = []

        if data.new_email:
            existing = await self.repository.get_user_by_email(data.new_email)
            if existing:
                raise email_already_registered_exception()
            authorized_user.email = data.new_email
            changed_fields.append("email")

        if data.new_password:
            authorized_user.password_hash = hash_password(data.new_password)
            changed_fields.append("password")

        user = await self.repository.update_user(authorized_user)

        await self._broadcast_sse_event(
            "user.account_updated",
            {
                "user_id": str(user.id),
                "changed_fields": changed_fields
            },
            user_id=user.id,
        )

        return user

    async def delete_account(
        self,
        user_id: UUID,
        authorized_user: User,
        data: DeleteAccount,
        response: Response,
    ) -> None:
        """Permanently delete the authenticated user's account.

        Args:
            user_id: The user id of the user you want to update
            authorized_user: The currently authenticated user instance.
            data: The deletion confirmation payload containing the user's password.
            response: Response used to clear auth cookies after deletion.

        """
        await self.verify_userid_and_auth_user(user_id, authorized_user, data.password)
        await self.repository.delete_user(authorized_user)

        await self._broadcast_sse_event(
            "user.account_deleted",
            {"user_id": str(authorized_user.id)},
            user_id=authorized_user.id,
        )

        clear_auth_cookies(response)
