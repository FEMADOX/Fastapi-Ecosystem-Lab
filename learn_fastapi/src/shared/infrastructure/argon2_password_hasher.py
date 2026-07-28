from argon2 import PasswordHasher as Argon2
from argon2.exceptions import InvalidHash, VerifyMismatchError

from learn_fastapi.src.users.domain.value_objects import PasswordHash


class Argon2PasswordHasher:
    """Hash a password using Argon2id."""

    def __init__(self) -> None:
        """Initialize the password hasher."""
        self._hasher = Argon2()

    def hash(self, password: str) -> PasswordHash:
        """Hash a password using Argon2id.

        Args:
            password: The plaintext password to hash.

        Returns:
            The hashed password as a string.

        """
        return PasswordHash(self._hasher.hash(password))

    def verify(self, password: str, password_hash: PasswordHash) -> bool:
        """Verify a password against its hash.

        Args:
            password: The plaintext password to verify.
            password_hash: The hashed password to compare against.

        Returns:
            True if the password is correct, False otherwise.

        """
        try:
            self._hasher.verify(password_hash, password)
        except (InvalidHash, VerifyMismatchError) as _:
            return False
        return True
