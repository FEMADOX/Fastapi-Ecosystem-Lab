from datetime import datetime

import jwt

from learn_fastapi.src.auth.application.ports import AccessTokenIssuer
from learn_fastapi.src.shared.domain.value_object import UserId


class PyJWTAccessTokenIssuer(AccessTokenIssuer):
    """PyJWT implementation of the access token issuance port."""

    def __init__(self, secret_key: str, algorithm: str) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def issue(self, user_id: UserId, expires_at: datetime) -> str:
        """Issue a signed JWT for a user with the given expiration."""
        return jwt.encode(
            {"sub": str(user_id), "exp": expires_at},
            self._secret_key,
            algorithm=self._algorithm,
        )
