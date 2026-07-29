from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=8, description="User password (min 8 characters)")


class UserUpdate(BaseModel):
    """Schema for updating the authenticated user's account."""

    current_password: str = Field(description="Current password to verify identity")
    new_email: EmailStr | None = Field(description="New email address", default=None)
    new_password: str | None = Field(
        min_length=8, description="New password (min 8 characters)", default=None
    )


class DeleteAccount(BaseModel):
    """Schema for confirming account deletion."""

    password: str = Field(description="Current password to confirm deletion")


class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: UUID = Field(description="User ID")
    email: str = Field(description="User email")
    is_active: bool = Field(description="Whether user is active", default=True)
    is_superuser: bool = Field(description="Whether user is a superuser", default=False)

    class ConfigDict:
        """Pydantic model config."""

        from_attributes = True
