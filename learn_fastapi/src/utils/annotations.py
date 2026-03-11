from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------
uuid_pk = Annotated[UUID, mapped_column(primary_key=True, default=uuid4)]
user_id_fk = Annotated[
    UUID,
    mapped_column(
        ForeignKey(
            "users.id",
            name="fk_items_user_id_users",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    ),
]

timestamp_created = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(tz=UTC)
    ),
]
timestamp_updated = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    ),
]
