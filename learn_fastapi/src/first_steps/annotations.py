import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import File, Form, UploadFile
from fastapi.params import Query
from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------

int_pk = Annotated[
    uuid.UUID,
    mapped_column(primary_key=True, default=uuid.uuid4),
]
str_indexed = Annotated[str, mapped_column(index=True)]
str_default = Annotated[str, mapped_column(default="No text provided")]
float_default = Annotated[float, mapped_column(default=0.00)]
str_url = Annotated[str, mapped_column(default="")]
timestamp_created = Annotated[
    datetime,
    mapped_column(
        nullable=False,
        default=lambda: datetime.now(tz=UTC),
    ),
]
timestamp_updated = Annotated[
    datetime,
    mapped_column(
        nullable=False,
        default=lambda: datetime.now(tz=UTC),
        onupdate=lambda: datetime.now(tz=UTC),
    ),
]

# ---------------------------------------------------------------------------
# Item Form field annotations
# ---------------------------------------------------------------------------

ItemName = Annotated[str, Form(description="The name of the item", min_length=3)]
ItemDescription = Annotated[
    str, Form(description="The description of the item", min_length=10)
]
ItemPrice = Annotated[float, Form(ge=0, description="The price of the item")]
ItemTax = Annotated[float, Form(ge=0, description="The tax of the item")]

# ---------------------------------------------------------------------------
# Image Query parameter annotation
# ---------------------------------------------------------------------------

ImageFilename = Annotated[str, Query(description="The filename of the image")]

# ---------------------------------------------------------------------------
# Image Form field annotations
# ---------------------------------------------------------------------------

ImageFile = Annotated[UploadFile, File(description="The image file to upload")]
ImageFileOptional = Annotated[
    UploadFile | None, File(description="Optional image file to upload")
]
ImageCaption = Annotated[str, Form(description="The caption for the image")]
