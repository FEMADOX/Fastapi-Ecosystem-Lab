from dataclasses import dataclass

from learn_fastapi.src.items.application.commands import (
    CreateItemCommand,
    CreateItemWithImageCommand,
    DeleteItemCommand,
    PatchItemCommand,
    UpdateItemCommand,
    UpdateItemImageCommand,
)
from learn_fastapi.src.items.application.queries import (
    GetItemQuery,
    GetOwnerItemQuery,
    ListOwnerItemsQuery,
)
from learn_fastapi.src.items.domain.entities import (
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.domain.errors import (
    ItemDuplicatedNameError,
    ItemNotFoundError,
    ItemNotFoundForUserError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.domain.ports import ImageStorage, ItemsRepository


@dataclass(slots=True)
class BaseItemsUseCase:
    """Base class for all `items` app use cases."""

    items_repository: ItemsRepository


class ListItemsUseCase(BaseItemsUseCase):
    """Use case for retrieving all items."""

    async def execute(self) -> list[PersistedItem]:
        """Execute the use case.

        Returns:
            A list of all items.

        """
        return await self.items_repository.list_items()


class GetItemUseCase(BaseItemsUseCase):
    """Use case for retrieving an item by its ID."""

    async def execute(self, query: GetItemQuery) -> PersistedItem:
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

    async def execute(self, query: ListOwnerItemsQuery) -> list[PersistedItem]:
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

    async def execute(self, query: GetOwnerItemQuery) -> PersistedItem:
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


class CreateItemUseCase(BaseItemsUseCase):
    """Use case for creating an item."""

    async def execute(self, command: CreateItemCommand) -> PersistedItem:
        """Execute the use case.

        Returns:
            The created item.

        """
        return await self.items_repository.create_item(
            command.owner_id, command.item_data
        )


class UpdateItemUseCase(BaseItemsUseCase):
    """Use case for updating an item."""

    async def execute(self, command: UpdateItemCommand) -> PersistedItem:
        """Execute the use case.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        item_updated = await self.items_repository.update_item(
            command.item_id, command.fields, command.is_superuser, command.owner_id
        )
        if item_updated is None:
            raise ItemNotFoundError
        return item_updated


class PatchItemUseCase(BaseItemsUseCase):
    """Use case for updating an item."""

    async def execute(self, command: PatchItemCommand) -> PersistedItem:
        """Execute the use case.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        item_patched = await self.items_repository.patch_item(
            command.item_id, command.fields, command.is_superuser, command.owner_id
        )
        if item_patched is None:
            raise ItemNotFoundError
        return item_patched


class DeleteItemUseCase(BaseItemsUseCase):
    """Use case for deleting an item."""

    async def execute(self, command: DeleteItemCommand) -> PersistedItem:
        """Execute the use case.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        owner_id = None if command.is_superuser else command.owner_id
        item_deleted = await self.items_repository.delete_item(
            command.item_id, owner_id
        )
        if not item_deleted:
            raise ItemNotFoundError
        return item_deleted


@dataclass(slots=True)
class BaseItemWithImageUseCase(BaseItemsUseCase):
    """Base class for all `items` app + image use cases."""

    image_storage: ImageStorage


class CreateItemWithImageUseCase(BaseItemWithImageUseCase):
    """Use case for creating an item with image."""

    async def execute(
        self, command: CreateItemWithImageCommand
    ) -> PersistedItemWithImage:
        """Execute the use case.

        Returns:
            The new item with image.

        Raises:
            ItemDuplicatedNameError: If the item is not found.

        """
        if await self.items_repository.get_item_by_name(command.name) is not None:
            raise ItemDuplicatedNameError

        new_image = await self.image_storage.upload(command.image_file, command.caption)

        return await self.items_repository.create_item_with_image(
            command.owner_id,
            command.name,
            command.description,
            command.price,
            command.tax,
            new_image,
        )


class UpdateItemImageUseCase(BaseItemWithImageUseCase):
    """Use case for updating the image of an item."""

    async def execute(self, command: UpdateItemImageCommand) -> PersistedItemWithImage:
        """Execute the use case.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        owner_id = None if command.is_superuser else command.owner_id
        item_id = command.item_id
        current_item = (
            await self.items_repository.get_item_by_id(item_id)
            if owner_id is None
            else await self.items_repository.get_owner_item(item_id, owner_id)
        )
        if current_item is None:
            raise ItemNotFoundError

        new_image = await self.image_storage.upload(command.image_file, command.caption)

        item_updated = await self.items_repository.update_item_with_image(
            command.item_id, owner_id, new_image
        )
        if item_updated is None:
            await self.image_storage.delete(new_image.public_id)
            raise ItemNotFoundError

        if current_item.image_public_id:
            await self.image_storage.delete(current_item.image_public_id)

        return item_updated
