from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, relationship

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    timestamp_created,
    timestamp_updated,
    uuid_pk,
)

from .annotations import (
    bool_default_false,
    bool_default_true,
    str_idx_unique,
)

if TYPE_CHECKING:
    from learn_fastapi.src.auth.models import RefreshToken
    from learn_fastapi.src.items.models import Item


class User(Base):
    """User model representing application users."""

    __tablename__ = "users"

    id: Mapped[uuid_pk]
    email: Mapped[str_idx_unique]
    password_hash: Mapped[str]
    is_active: Mapped[bool_default_true]
    is_superuser: Mapped[bool_default_false]
    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    items: Mapped[list[Item]] = relationship(
        "Item", back_populates="user", cascade="all, delete-orphan"
    )

    if TYPE_CHECKING:
        id: UUID
        password_hash: str
        email: str
        password_hash: str
        is_active: bool
        is_superuser: bool
