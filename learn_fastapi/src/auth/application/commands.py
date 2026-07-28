from dataclasses import dataclass

from learn_fastapi.src.auth.domain.entities import PersistedRefreshToken
from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class CreateRefreshTokenCommand:
    owner_id: UserId


@dataclass(frozen=True, slots=True)
class IssueAccessTokenCommand:
    owner_id: UserId


@dataclass(frozen=True, slots=True)
class RevokeRefreshTokensCommand:
    owner_id: UserId


@dataclass(frozen=True, slots=True)
class RevokeRefreshTokenCommand:
    token: PersistedRefreshToken
    token_raw: str
