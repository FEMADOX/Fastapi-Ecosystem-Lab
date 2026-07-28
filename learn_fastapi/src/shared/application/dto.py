from dataclasses import dataclass

from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.users.domain.value_objects import PasswordHash


@dataclass(frozen=True, slots=True)
class CurrentActor:
    id: UserId
    is_superuser: bool


@dataclass(frozen=True, slots=True)
class AuthenticatedAccount:
    id: UserId
    email: str
    password_hash: PasswordHash
    is_active: bool
    is_superuser: bool

    def to_actor(self) -> CurrentActor:
        return CurrentActor(id=self.id, is_superuser=self.is_superuser)
