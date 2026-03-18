from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, relationship

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    timestamp_created,
    user_id_fk,
    uuid_pk,
)

from .annotations import (
    expiration,
    revoked,
    token_hash,
)

if TYPE_CHECKING:
    from learn_fastapi.src.users.models import User


class RefreshToken(Base):
    """Refresh token storage for JWT token rotation."""

    __tablename__ = "refresh_tokens"

    id: Mapped[uuid_pk]
    user_id: Mapped[user_id_fk]
    token_hash: Mapped[token_hash]
    expires_at: Mapped[expiration]
    created_at: Mapped[timestamp_created]
    revoked_at: Mapped[revoked]

    user: Mapped[User] = relationship("User", back_populates="refresh_tokens")

    if TYPE_CHECKING:
        id: UUID
        user_id: UUID
        token_hash: str
        expires_at: datetime
        revoked_at: datetime | None
