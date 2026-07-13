from dataclasses import dataclass

from learn_fastapi.src.items.application.queries import (
    GetItemQuery,
    GetOwnerItemQuery,
    ListOwnerItemsQuery,
)
from learn_fastapi.src.items.domain.entities import Item
from learn_fastapi.src.items.domain.errors import (
    ItemNotFoundError,
    ItemNotFoundForUserError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.domain.ports import ItemsRepository


@dataclass(slots=True)
class BaseItemsUseCase:
    """Base class for all `items` app use cases."""

    items_repository: ItemsRepository


class ListItemsUseCase(BaseItemsUseCase):
    """Use case for retrieving all items."""

    async def execute(self) -> list[Item]:
        """Execute the use case.

        Returns:
            A list of all items.

        """
        return await self.items_repository.list_items()


class GetItemUseCase(BaseItemsUseCase):
    """Use case for retrieving an item by its ID."""

    async def execute(self, query: GetItemQuery) -> Item:
        """Execute the use case.

        Returns:
            The requested item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        item = await self.items_repository.get_item_by_id(query.item_id)
        if not item:
            raise ItemNotFoundError
        return item


class ListOwnerItemsUseCase(BaseItemsUseCase):
    """Use case for retrieving all items belonging to a specific owner."""

    async def execute(self, query: ListOwnerItemsQuery) -> list[Item]:
        """Execute the use case.

        Returns:
            A list of items belonging to the specified owner.

        Raises:
            ItemsNotFoundForUserError: If no items are found for the user.

        """
        items = await self.items_repository.list_owner_items(query.owner_id)
        if not len(items) > 0:
            raise ItemsNotFoundForUserError
        return items


class GetOwnerItemUseCase(BaseItemsUseCase):
    """Use case for retrieving an item belonging to a specific owner."""

    async def execute(self, query: GetOwnerItemQuery) -> Item:
        """Execute the use case.

        Returns:
            The requested item.

        Raises:
            ItemNotFoundForUserError: If the item is not found for the user.

        """
        item = await self.items_repository.get_owner_item(query.item_id, query.owner_id)
        if not item:
            raise ItemNotFoundForUserError
        return item
