from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password (min 8 characters)")


class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: UUID = Field(description="User ID")
    email: str = Field(description="User email")
    is_active: bool = Field(description="Whether user is active")
    is_superuser: bool = Field(description="Whether user is a superuser")

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    """Schema for JWT token payload."""

    sub: str = Field(description="Subject (usually user email)")
    exp: int | None = Field(description="Expiration timestamp", default=None)


class Token(BaseModel):
    """Schema for token response."""

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse | None = Field(description="User information", default=None)
