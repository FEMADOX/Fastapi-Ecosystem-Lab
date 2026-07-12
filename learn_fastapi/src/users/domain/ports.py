from typing import Protocol

from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.entities import User as UserDomain


class UsersRepository(Protocol):
    """Protocol for user repository operations."""

    async def get_user_by_id(self, user_id: UserId) -> UserDomain | None: ...
    async def get_user_by_email(self, user_email: str) -> UserDomain | None: ...

    # async def update_user(self, user_id: UserId) -> User: ...
    # async def delete_user(self, user_id: UserId) -> User: ...
