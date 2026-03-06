import os
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production-use-env-var!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hasher instance
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id.

    Returns:
        The hashed password as a string.

    """
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash.

    Returns:
        True if the password is correct, False otherwise.

    """
    try:
        ph.verify(password_hash, password)
        return True
    except InvalidHash, VerifyMismatchError:
        return False


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Returns:
        The encoded JWT token as a string.

    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(tz=UTC) + expires_delta
    else:
        expire = datetime.now(tz=UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT access token.

    Returns:
        The token payload if valid, or None if invalid.

    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
