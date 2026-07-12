from dataclasses import dataclass

from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(slots=True, frozen=True)
class GetRefreshTokenQuery:
    """Query for retrieving a refresh token by the owner ID."""

    owner_id: UserId


@dataclass(slots=True, frozen=True)
class GetUserByRefreshTokenQuery:
    """Query for retrieving the owner by the refresh token."""

    refresh_token: str
