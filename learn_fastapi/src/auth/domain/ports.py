from datetime import datetime
from typing import Protocol

from learn_fastapi.src.auth.domain.entities import (
    PersistedRefreshToken,
)
from learn_fastapi.src.shared.domain.value_object import UserId


class AuthRepository(Protocol):
    """Protocol for auth repository operations."""

    async def get_refresh_token(
        self, owner_id: UserId
    ) -> PersistedRefreshToken | None: ...
    async def create_refresh_token(
        self,
        user_id: UserId,
        token_hash: str,
        expires_at: datetime,
    ) -> PersistedRefreshToken: ...
    async def revoke_refresh_tokens(self, owner_id: UserId) -> None: ...
    async def revoke_refresh_token(
        self, token: PersistedRefreshToken, token_raw: str
    ) -> None: ...
