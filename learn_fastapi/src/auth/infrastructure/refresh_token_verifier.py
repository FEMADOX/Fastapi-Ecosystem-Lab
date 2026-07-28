from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError

_ph = PasswordHasher()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    try:
        _ph.verify(token_hash, token)
        return True
    except InvalidHash, VerifyMismatchError:
        return False
