from typing import Protocol

from learn_fastapi.src.auth.domain.entities import RefreshToken as RefreshTokenDomain
from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.entities import User as UserDomain


class AuthRepository(Protocol):
    """Protocol for auth repository operations."""

    async def get_refresh_token(
        self, owner_id: UserId
    ) -> RefreshTokenDomain | None: ...
    async def get_user_from_refresh_token(
        self, refresh_token: str
    ) -> UserDomain | None: ...
