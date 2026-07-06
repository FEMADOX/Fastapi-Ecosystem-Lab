from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, frozen=True)
class ItemDTO:
    id: UUID | None
    owner_id: UUID
    name: str
    description: str
    price: float
    tax: float
    image_url: str | None = None
