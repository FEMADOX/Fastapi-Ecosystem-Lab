from datetime import datetime
from typing import Annotated

from fastapi import Header
from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------

token_hash = Annotated[str, mapped_column(unique=True, index=True, nullable=False)]
expiration = Annotated[datetime, mapped_column(DateTime(timezone=True), nullable=False)]
revoked = Annotated[
    datetime | None, mapped_column(DateTime(timezone=True), nullable=True, default=None)
]

# Annotations for routes
X_CSRF_TOKEN = Annotated[str, Header(alias="X-CSRF-Token")]
