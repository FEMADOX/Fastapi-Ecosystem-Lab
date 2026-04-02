from datetime import UTC, datetime

from pydantic import BaseModel, Field

from .config import auth_config


class TokenData(BaseModel):
    """Schema for JWT token payload."""

    sub: str = Field(description="Subject (usually user email)")
    exp: datetime | None = Field(
        description="Expiration timestamp",
        default=datetime.now(tz=UTC).astimezone() + auth_config.access_token_expire,
    )


class Token(BaseModel):
    """Schema for token response."""

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(description="Token type", default="bearer")
    expires_in: int = Field(description="Expiration timestamp")
    csrf_token: str = Field(description="CSRF token")


# TODO (FENYXZ): Create a Schema for API v2 that includes:
#   - expires_in => access_token_expires_in: int = Field(description="Access token expiration timestamp")
#   - refresh_token: str = Field(description="JWT refresh token")
#   - refresh_token_expires_in: int = Field(description="Refresh token expiration timestamp")
