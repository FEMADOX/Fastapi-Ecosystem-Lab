from datetime import datetime

from dateutil.tz import UTC
from pydantic import BaseModel, Field

from .config import auth_config


class TokenData(BaseModel):
    """Schema for JWT token payload."""

    sub: str = Field(description="Subject (usually user email)")
    exp: datetime | None = Field(
        description="Expiration timestamp",
        default=datetime.now(tz=UTC) + auth_config.access_token_expire,
    )


class Token(BaseModel):
    """Schema for token response."""

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(description="Token type", default="bearer")
    expires_in: int = Field(description="Expiration timestamp")
    csrf_token: str = Field(description="CSRF token")
