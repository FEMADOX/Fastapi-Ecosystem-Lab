from sqlalchemy.orm import Mapped

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    int_pk,
    timestamp_created,
    timestamp_updated,
)

from .annotations import (
    float_default,
    str_default,
    str_indexed,
    str_url,
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
