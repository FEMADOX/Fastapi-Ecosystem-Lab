from argon2 import PasswordHasher as Argon2

from learn_fastapi.src.auth.application.ports import RefreshTokenHasher


class Argon2RefreshTokenHasher(RefreshTokenHasher):
    """Argon2 implementation for persisted refresh token secrets."""

    def __init__(self) -> None:
        self._hasher = Argon2()

    def hash(self, token: str) -> str:
        """Hash a raw refresh token before persistence."""
        return self._hasher.hash(token)
