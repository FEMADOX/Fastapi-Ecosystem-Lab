import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import UUID, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from learn_fastapi.src.database import Base

if TYPE_CHECKING:
    pass


class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(index=True)
    description: Mapped[str] = mapped_column(default="No description provided")
    price: Mapped[float] = mapped_column(default=0.00)
    tax: Mapped[float] = mapped_column(default=0.00)
    image_url: Mapped[str] = mapped_column(default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now(tz=UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(tz=UTC),
        onupdate=datetime.now(tz=UTC),
    )
