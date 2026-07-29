from pydantic import BaseModel

from learn_fastapi.src.items.application.ports import PublishableItem
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId
from learn_fastapi.src.shared.infrastructure.json_types import (
    JSONObject,
    model_dump_json_object,
)
from learn_fastapi.src.sse.manager import sse_manager


class ItemEventRecord(BaseModel):
    """Public payload sent from SSE for an item."""

    id: ItemId
    user_id: UserId
    name: str
    description: str
    price: float
    tax: float
    image_url: str | None
    image_public_id: str | None

    @classmethod
    def from_domain(cls, item: PublishableItem) -> ItemEventRecord:
        return cls(
            id=item.id,
            user_id=item.owner_id,
            name=item.name,
            description=item.description,
            price=item.price,
            tax=item.tax,
            image_url=item.image_url,
            image_public_id=item.image_public_id,
        )


class SSEItemEventPublisher:
    """Public the item event using the SSE manager."""

    @staticmethod
    def _build_payload(item: PublishableItem) -> JSONObject:
        return model_dump_json_object(ItemEventRecord.from_domain(item))

    async def _broadcast_user(self, event: str, item: PublishableItem) -> None:
        await sse_manager.broadcast_user(
            item.owner_id, event, self._build_payload(item)
        )

    async def item_created(self, item: PublishableItem) -> None:
        payload = self._build_payload(item)

        await sse_manager.broadcast_global("item.created", payload)
        await sse_manager.broadcast_user(item.owner_id, "item.created", payload)

    async def item_updated(self, item: PublishableItem) -> None:
        await self._broadcast_user("item.updated", item)

    async def item_image_updated(self, item: PublishableItem) -> None:
        await self._broadcast_user(
            "item.image_updated",
            item,
        )

    async def item_deleted(self, item: PublishableItem) -> None:
        await self._broadcast_user("item.deleted", item)
