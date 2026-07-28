from dataclasses import dataclass
from datetime import datetime

from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(frozen=True, slots=True)
class IssuedAccessToken:
    """Access token data returned by the token issuance workflow."""

    value: str
    expires_at: datetime
    expires_in: int


@dataclass(frozen=True, slots=True)
class IssuedRefreshToken:
    """Refresh token data returned by the refresh token creation workflow."""

    value: str
    expires_at: datetime
    expires_in: int


@dataclass(frozen=True, slots=True)
class LoginResult:
    """Application-level result of a successful login flow."""

    access_token: str
    access_expires_in: int
    refresh_token_raw: str
    refresh_expires_in: int
    user_id: UserId
