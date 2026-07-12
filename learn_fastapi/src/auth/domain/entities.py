from dataclasses import dataclass
from datetime import datetime

from learn_fastapi.src.shared.domain.value_object import RefreshTokenId, UserId


@dataclass(frozen=True, slots=True)
class RefreshToken:
    """Domain entity representing a refresh token."""

    id: RefreshTokenId | None
    owner_id: UserId
    token_hash: str
    expires_at: datetime | None
    created_at: datetime | None
    revoked_at: datetime | None


@dataclass(frozen=True, slots=True)
class PersistedRefreshToken:
    """Domain entity representing a persisted refresh token."""

    id: RefreshTokenId
    owner_id: UserId
    token_hash: str
