import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

from learn_fastapi.src.auth.schema import TokenData
from learn_fastapi.src.config import settings

# Configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

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


def create_access_token(token_data: TokenData) -> str:
    """Create a JWT access token.

    Returns:
        The encoded JWT token as a string.

    """
    to_encode = token_data.model_dump()

    return jwt.encode(to_encode, SECRET_KEY.get_secret_value(), algorithm=ALGORITHM)


def verify_access_token(token: str) -> TokenData | None:
    """Verify a JWT access token and return its data.

    Args:
        token: The JWT token string to verify.

    Returns:
        A TokenData instance if the token is valid, or None if invalid.

    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY.get_secret_value(),
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None
    # data = {"sub": payload.get("sub"), "exp": payload.get("exp")}
    return TokenData(sub=payload["sub"], exp=payload["exp"])
