from dataclasses import dataclass

from learn_fastapi.src.items.application.commands import (
    CreateItemCommand,
    CreateItemWithImageCommand,
    DeleteItemCommand,
    PatchItemCommand,
    UpdateItemCommand,
    UpdateItemImageCommand,
)
from learn_fastapi.src.items.application.ports import (
    ImageStorage,
    ItemsCache,
    ItemsEventPublisher,
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
    ItemsForbiddenOwnerAccessError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.domain.ports import ItemsRepository
from learn_fastapi.src.shared.application.dto import CurrentActor
from learn_fastapi.src.shared.domain.value_object import UserId


@dataclass(slots=True)
class BaseItemsUseCase:
    """Base class for all `items` app use cases."""

    items_repository: ItemsRepository
    cache: ItemsCache


class ListItemsUseCase(BaseItemsUseCase):
    """Use case for retrieving all items."""

    async def execute(self) -> list[PersistedItem]:
        """Execute the use case.

        Returns:
            A list of all items.

        """
        cached_items = await self.cache.list_items()
        if cached_items:
            return cached_items

        items = await self.items_repository.list_items()

        await self.cache.set_items(items)

        return items


class GetItemUseCase(BaseItemsUseCase):
    """Use case for retrieving an item by its ID."""

    async def execute(self, query: GetItemQuery) -> PersistedItem:
        """Execute the use case.

        Returns:
            The requested item.

        Raises:
            ItemNotFoundError: If the item is not found.

        """
        item_id = query.item_id
        cached_item = await self.cache.get_item(item_id)
        if cached_item is not None:
            return cached_item

        item = await self.items_repository.get_item_by_id(item_id)
        if not item:
            raise ItemNotFoundError

        await self.cache.set_item(item)

        return item


def _resolve_owner_id(
    actor: CurrentActor,
    requested_owner_id: UserId | None,
) -> UserId:
    """Resolve the effective item owner from the authenticated actor.

    Returns:
        UserId: The owner id.

    Raises:
        ItemsForbiddenOwnerAccessError: Raises when the item doesn't belong to the user.

    """
    if requested_owner_id is None or requested_owner_id == actor.id:
        return actor.id
    if not actor.is_superuser:
        raise ItemsForbiddenOwnerAccessError
    return requested_owner_id


class ListOwnerItemsUseCase(BaseItemsUseCase):
    """Use case for retrieving all items belonging to a specific owner."""

    async def execute(self, query: ListOwnerItemsQuery) -> list[PersistedItem]:
        """Execute the use case.

        Returns:
            A list of items belonging to the specified owner.

        Raises:
            ItemsNotFoundForUserError: If no items are found for the user.

        """
        owner_id = _resolve_owner_id(query.actor, query.owner_id)
        cached_items = await self.cache.list_owner_items(owner_id)
        if cached_items:
            return cached_items

        items = await self.items_repository.list_owner_items(owner_id)
        if not len(items) > 0:
            raise ItemsNotFoundForUserError

        await self.cache.set_owner_items(owner_id, items)

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
        item_id = query.item_id
        owner_id = _resolve_owner_id(query.actor, query.owner_id)
        cached_item = await self.cache.get_owner_item(item_id, owner_id)
        if cached_item:
            return cached_item

        item = await self.items_repository.get_owner_item(item_id, owner_id)
        if not item:
            raise ItemNotFoundForUserError

        await self.cache.set_owner_item(item)

        return item


@dataclass(slots=True)
class BaseItemsEventPublisherUseCase(BaseItemsUseCase):
    """Use case for all the use cases that use event publisher."""

    event_publisher: ItemsEventPublisher


class CreateBaseItemsUseCase(BaseItemsEventPublisherUseCase):
    """Use case for creating an item."""

    async def execute(self, command: CreateItemCommand) -> PersistedItem:
        """Execute the use case.

        Returns:
            The created item.

        """
        new_item = await self.items_repository.create_item(
            command.owner_id, command.item_data
        )

        await self.cache.invalidate_all()

        await self.event_publisher.item_created(new_item)

        return new_item


class UpdateBaseItemsUseCase(BaseItemsEventPublisherUseCase):
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

        await self.cache.invalidate_all()

        await self.event_publisher.item_updated(item_updated)

        return item_updated


class PatchItemUseCaseBase(BaseItemsEventPublisherUseCase):
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

        await self.cache.invalidate_all()

        await self.event_publisher.item_updated(item_patched)

        return item_patched


class DeleteItemUseCaseBase(BaseItemsEventPublisherUseCase):
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

        await self.cache.invalidate_all()

        await self.event_publisher.item_deleted(item_deleted)

        return item_deleted


@dataclass(slots=True)
class BaseItemWithImageUseCaseBase(BaseItemsEventPublisherUseCase):
    """Base class for all `items` app + image use cases."""

    image_storage: ImageStorage


class CreateItemWithImageUseCase(BaseItemWithImageUseCaseBase):
    """Use case for creating an item with image."""

    async def execute(
        self, command: CreateItemWithImageCommand
    ) -> PersistedItemWithImage:
        """Execute the use case.

        Returns:
            The new item with image.

        Raises:
            ItemDuplicatedNameError: If the item is not found.
            InvalidImageUploadError: Filename is for image is required.

        """
        if await self.items_repository.get_item_by_name(command.name) is not None:
            raise ItemDuplicatedNameError

        new_image = await self.image_storage.upload(command.image_file, command.caption)

        await self.cache.invalidate_all()

        new_item = await self.items_repository.create_item_with_image(
            command.owner_id,
            command.name,
            command.description,
            command.price,
            command.tax,
            new_image,
        )

        await self.event_publisher.item_created(new_item)

        return new_item


class UpdateItemImageUseCase(BaseItemWithImageUseCaseBase):
    """Use case for updating the image of an item."""

    async def execute(self, command: UpdateItemImageCommand) -> PersistedItemWithImage:
        """Execute the use case.

        Returns:
            The updated item.

        Raises:
            ItemNotFoundError: If the item is not found.
            InvalidImageUploadError: If the uploaded image is invalid.

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

        await self.cache.invalidate_all()

        if item_updated is None:
            await self.image_storage.delete(new_image.public_id)
            raise ItemNotFoundError

        if current_item.image_public_id:
            await self.image_storage.delete(current_item.image_public_id)

        await self.event_publisher.item_image_updated(item_updated)

        return item_updated
