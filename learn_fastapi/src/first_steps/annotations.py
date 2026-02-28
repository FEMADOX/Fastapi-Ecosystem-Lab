from typing import Annotated

from fastapi import File, Form, UploadFile
from fastapi.params import Query

# Item Form field annotations
ItemName = Annotated[str, Form(description="The name of the item", min_length=3)]
ItemDescription = Annotated[
    str, Form(description="The description of the item", min_length=10)
]
ItemPrice = Annotated[float, Form(ge=0, description="The price of the item")]
ItemTax = Annotated[float, Form(ge=0, description="The tax of the item")]

# Image Query parameter annotation
ImageFilename = Annotated[str, Query(description="The filename of the image")]

# Image Form field annotations
ImageFile = Annotated[UploadFile, File(description="The image file to upload")]
ImageFileOptional = Annotated[
    UploadFile | None, File(description="Optional image file to upload")
]
ImageCaption = Annotated[str, Form(description="The caption for the image")]
