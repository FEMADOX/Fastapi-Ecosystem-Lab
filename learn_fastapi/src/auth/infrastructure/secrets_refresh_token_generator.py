import secrets

from learn_fastapi.src.auth.application.ports import RefreshTokenGenerator


class SecretsRefreshTokenGenerator(RefreshTokenGenerator):
    """Generate cryptographically secure refresh token secrets."""

    def generate(self) -> str:
        """Return a URL-safe refresh token secret."""
        return secrets.token_urlsafe(32)
