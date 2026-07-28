from datetime import datetime
from typing import Protocol

from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.entities import PersistedUser


class AuthEventPublisher(Protocol):
    """Protocol for sse in the auth operations."""

    async def auth_registered(self, user: PersistedUser) -> None: ...
    async def auth_logged_in(self, user_id: UserId) -> None: ...
    async def auth_logged_out(self, user_id: UserId) -> None: ...


class AccessTokenIssuer(Protocol):
    """Application port for issuing access tokens."""

    def issue(self, user_id: UserId, expires_at: datetime) -> str: ...


class RefreshTokenGenerator(Protocol):
    """Application port for generating raw refresh token secrets."""

    def generate(self) -> str: ...


class RefreshTokenHasher(Protocol):
    """Application port for hashing refresh token secrets."""

    def hash(self, token: str) -> str: ...
