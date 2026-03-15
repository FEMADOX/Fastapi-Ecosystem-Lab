import secrets
from datetime import UTC, datetime

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from starlette.responses import Response

from learn_fastapi.src.auth.config import auth_config
from learn_fastapi.src.auth.schema import TokenData

# Configuration
SECRET_KEY = auth_config.secret_key
ALGORITHM = auth_config.algorithm
ACCESS_TOKEN_EXPIRE = auth_config.access_token_expire

# Password hasher instance
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2id.

    Args:
        password: The plaintext password to hash.

    Returns:
        The hashed password as a string.

    """
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash.

    Args:
        password: The plaintext password to verify.
        password_hash: The hashed password to compare against.

    Returns:
        True if the password is correct, False otherwise.

    """
    try:
        ph.verify(password_hash, password)
        return True
    except (InvalidHash, VerifyMismatchError) as _:
        return False


def create_access_token(token_data: TokenData) -> str:
    """Create a JWT access token.

    Args:
        token_data: A TokenData instance containing the token payload.

    Returns:
        The encoded JWT token as a string.

    """
    to_encode = token_data.model_dump()

    return jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """Decode a JWT access token without verification.

    Args:
        token: The JWT token string to decode.

    Returns:
        The decoded token payload as a dictionary, or None if decoding fails.

    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError:
        return None


def generate_refresh_token() -> str:
    """Generate a secure random string for refresh token.

    Returns:
        URL-safe random token (32 bytes * 43 chars base64).

    """
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using SHA-256.

    Args:
        token: The plaintext refresh token to hash.

    Returns:
        Use Argon2id to hash the refresh token for secure storage.

    """
    return ph.hash(token)


def verify_access_token(token: str) -> TokenData | None:
    """Verify a JWT access token and return its data.

    Args:
        token: The JWT token string to verify.

    Returns:
        A TokenData instance if the token is valid, or None if invalid.

    """
    payload = decode_access_token(token)
    if not payload:
        return None
    return TokenData(sub=payload["sub"], exp=payload["exp"])


def verify_refresh_token(token: str, token_hash: str) -> bool:
    """Verify a refresh token against its hash.

    Args:
        token: The plaintext refresh token to verify.
        token_hash: The hashed refresh token to compare against.

    Returns:
        True if the refresh token is correct, False otherwise.

    """
    try:
        ph.verify(token_hash, token)
        return True
    except (InvalidHash, VerifyMismatchError) as _:
        return False


def get_refresh_token_expiration() -> datetime:
    """Calculate the expiration datetime for a refresh token.

    Returns:
        The expiration datetime for a refresh token.

    """
    return datetime.now(tz=UTC) + auth_config.refresh_token_expire


def set_auth_cookies(response: Response, refresh_token: str, csrf_token: str) -> None:
    """Set secure cookies for refresh token and CSRF token.

    Args:
        response: The FastAPI Response object to set cookies on.
        refresh_token: The JWT refresh token to store in a cookie.
        csrf_token: The CSRF token to store in a cookie.

    """
    max_age = int(auth_config.refresh_token_expire.total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=auth_config.cookie_secure,
        samesite=auth_config.cookie_samesite,
        max_age=max_age,  # 7 days
        path="/auth",
        domain=auth_config.cookie_domain,
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        # httponly=False,
        secure=auth_config.cookie_secure,
        samesite=auth_config.cookie_samesite,
        max_age=max_age,
        path="/auth",
        domain=auth_config.cookie_domain,
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear the authentication cookies for refresh token and CSRF token.

    Args:
        response: The FastAPI Response object to delete cookies from.

    """
    response.delete_cookie(
        key="refresh_token", path="/auth", domain=auth_config.cookie_domain
    )
    response.delete_cookie(
        key="csrf_token", path="/auth", domain=auth_config.cookie_domain
    )
