from datetime import timedelta
from typing import Literal

from learn_fastapi.src.config import Settings, settings


class AuthConfig(Settings):
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Set to True in production when using HTTPS
    cookie_secure: bool = settings.environment == "production"
    # Use "none" if your frontend is on a different domain,
    # "strict" for same-site only and "lax" for a balance between security and usability
    cookie_samesite: Literal["strict", "lax", "none"] = "lax"
    # Set to your domain in production, or None for localhost
    cookie_domain: str | None = None

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(days=self.refresh_token_expire_days)


auth_config = AuthConfig()  # ty:ignore[missing-argument]
