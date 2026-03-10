from sqlalchemy.orm import Mapped, mapped_column, relationship

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    int_pk,
    timestamp_created,
    timestamp_updated,
)

from .annotations import (
    bool_default_false,
    bool_default_true,
    expiration,
    revoked,
    str_idx_unique,
    token_hash,
    user_id_fk,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    email: Mapped[str_idx_unique]
    password_hash: Mapped[str]
    phone_number: Mapped[str | None] = mapped_column(nullable=True)
    is_active: Mapped[bool_default_true]
    is_superuser: Mapped[bool_default_false]
    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]

    refresh_tokens: Mapped[list[RefreshToken]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """Refresh token storage for JWT token rotation."""

    __tablename__ = "refresh_tokens"

    id: Mapped[int_pk]
    user_id: Mapped[user_id_fk]
    token_hash: Mapped[token_hash]
    expires_at: Mapped[expiration]
    created_at: Mapped[timestamp_created]
    revoked_at: Mapped[revoked]

    user: Mapped[User] = relationship(User, back_populates="refresh_tokens")
