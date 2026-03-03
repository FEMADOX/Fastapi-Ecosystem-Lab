from sqlalchemy.orm import Mapped

from learn_fastapi.src.database import Base
from learn_fastapi.src.first_steps.annotations import (
    float_default,
    int_pk,
    str_default,
    str_indexed,
    str_url,
    timestamp_created,
    timestamp_updated,
)


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int_pk]
    name: Mapped[str_indexed]
    description: Mapped[str_default]
    price: Mapped[float_default]
    tax: Mapped[float_default]
    image_url: Mapped[str_url]
    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]
