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


# class Image(BaseModel):
#     name: str | None = Field(description="The filename of the image", default=None)
#     description: str = Field(
#         description="The description of the image", default="No description provided"
#     )
#     content_type: str | None = Field(
#         description="The MIME type of the image", default=None
#     )
#     url: str = Field(description="The url of the image", default="")


# class Image(Base):
#     __tablename__ = "images"
#
#     name: Mapped[str] = mapped_column(default=None)
#     description: Mapped[str] = mapped_column(default="No description provided")
#     content_type: Mapped[str] = mapped_column(default=None)
#     url: Mapped[str] = mapped_column(description="The url of the image", default="")

# id = Column(UUID, primary_key=True, index=True)
# name = Column(String, index=True)
# description = Column(String, index=True, default="No description provided")
# price = Column(DECIMAL(2), default=0.00)
# tax = Column(DECIMAL(2), default=0.00)
# image_url = Column(String, default="")
# created_at = Column(DateTime, nullable=False, default=datetime.now())
# updated_at = Column(
#     DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now()
# )
