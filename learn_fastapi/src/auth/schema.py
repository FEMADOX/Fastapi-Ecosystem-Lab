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


class TokenV2(BaseModel):
    """Schema for token response v2."""

    access_token: str = Field(description="JWT access token")
    access_expires_in: int = Field(description="Expiration timestamp of access token")
    access_token_type: str = Field(
        description="Token type of access token", default="bearer"
    )
    refresh_token: str = Field(description="JWT refresh token")
    refresh_expires_in: int = Field(description="Expiration timestamp of refresh token")
    csrf_token: str = Field(description="CSRF token")
