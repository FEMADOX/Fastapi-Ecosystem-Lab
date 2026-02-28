from uuid import UUID

from pydantic import BaseModel, Field


class Image(BaseModel):
    name: str | None = Field(description="The filename of the image", default=None)
    description: str = Field(
        description="The description of the image", default="No description provided"
    )
    content_type: str | None = Field(
        description="The MIME type of the image", default=None
    )
    url: str = Field(description="The url of the image", default="")


class Item(BaseModel):
    id: UUID | None = Field(
        description="The id of the item",
        default=None,
        exclude=False,
    )
    name: str = Field(description="The name of the item", min_length=3)
    description: str = Field(
        description="The description of the item",
        default="No description provided",
        min_length=10,
    )
    price: float = Field(ge=0, description="The price of the item")
    tax: float = Field(ge=0, description="The tax of the item", default=0.00)
    # images: list[Image] | list[None] = Field(
    #     description="The list of images of the item",
    #     default_factory=list
    # )
    image_url: str | None = Field(description="The url of the image", default=None)
