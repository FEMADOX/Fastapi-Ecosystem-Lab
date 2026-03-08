from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import Header
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------

# users table
str_idx_unique = Annotated[str, mapped_column(unique=True, index=True)]
bool_default_true = Annotated[bool, mapped_column(default=True)]
bool_default_false = Annotated[bool, mapped_column(default=False)]

# refresh_tokens table
user_id_fk = Annotated[
    UUID, mapped_column(ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"))
]
token_hash = Annotated[str, mapped_column(unique=True, index=True, nullable=False)]
expiration = Annotated[datetime, mapped_column(DateTime(timezone=True), nullable=False)]
revoked = Annotated[
    datetime | None, mapped_column(DateTime(timezone=True), nullable=True, default=None)
]

# Annotations for routes

X_CSRF_TOKEN = Annotated[str, Header(alias="X-CSRF-Token")]
