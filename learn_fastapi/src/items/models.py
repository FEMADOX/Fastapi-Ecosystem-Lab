from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Mapped, relationship

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    timestamp_created,
    timestamp_updated,
    user_id_fk,
    uuid_pk,
)

from .annotations import (
    float_default,
    str_default,
    str_indexed,
    str_url,
)

if TYPE_CHECKING:
    from learn_fastapi.src.users.models import User


class Item(Base):
    __tablename__ = "items"

    id: Mapped[uuid_pk]
    name: Mapped[str_indexed]
    description: Mapped[str_default]
    price: Mapped[float_default]
    tax: Mapped[float_default]
    image_url: Mapped[str_url]
    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]
    user_id: Mapped[user_id_fk]

    user: Mapped[User] = relationship("User", back_populates="items")

    if TYPE_CHECKING:
        id: UUID
