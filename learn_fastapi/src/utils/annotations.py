import uuid
from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------
int_pk = Annotated[uuid.UUID, mapped_column(primary_key=True, default=uuid.uuid4)]

timestamp_created = Annotated[
    datetime,
    mapped_column(nullable=False, default=lambda: datetime.now(tz=UTC)),
]
timestamp_updated = Annotated[
    datetime,
    mapped_column(
        nullable=False,
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    ),
]
