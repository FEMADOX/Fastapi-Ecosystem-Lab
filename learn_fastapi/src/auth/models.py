from sqlalchemy.orm import Mapped

from learn_fastapi.src.database import Base
from learn_fastapi.src.utils.annotations import (
    int_pk,
    timestamp_created,
    timestamp_updated,
)

from .annotations import bool_default_false, bool_default_true, str_idx_unique


class User(Base):
    __tablename__ = "users"

    id: Mapped[int_pk]
    email: Mapped[str_idx_unique]
    password_hash: Mapped[str]
    is_active: Mapped[bool_default_true]
    is_superuser: Mapped[bool_default_false]
    created_at: Mapped[timestamp_created]
    updated_at: Mapped[timestamp_updated]
