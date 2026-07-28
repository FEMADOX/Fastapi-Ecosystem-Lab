from datetime import datetime
from typing import Protocol

from learn_fastapi.src.users.domain.value_objects import PasswordHash


class PasswordHasher(Protocol):
    """Application port for password hashing."""

    def hash(self, password: str) -> PasswordHash: ...
    def verify(self, password: str, password_hash: PasswordHash) -> bool: ...


class Clock(Protocol):
    """Application port for obtaining the current time."""

    def now(self) -> datetime: ...
