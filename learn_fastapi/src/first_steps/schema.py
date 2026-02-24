from pydantic import BaseModel, Field


class Item(BaseModel):
    name: str = Field(
        description="The name of the item",
        min_length=3,
    )
    description: str = Field(
        description="The description of the item",
        default="No description provided",
        min_length=10,
    )
    price: float = Field(ge=0, description="The price of the item")
    tax: float = Field(ge=0, description="The tax of the item", default=0.00)
