from uuid import UUID

from fastapi import UploadFile

from learn_fastapi.src.auth.models import User
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.exceptions import (
    item_not_found_exception,
    item_not_found_or_not_belong_to_user_exception,
)
from learn_fastapi.src.items.repository import ItemRepository
from learn_fastapi.src.items.schema import ItemSchema, ItemUpdateSchema
from learn_fastapi.src.items.utils import save_image_file


class ItemService:
    """Service class for Item business logic."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository = ItemRepository(session)

    async def get_all_items(self) -> list[ItemSchema]:
        """Return all items in the database as serialized schemas.

        Returns:
            A list of every ItemSchema (maybe empty).

        """
        items = await self.repository.get_all_items()
        return [ItemSchema(**item.__dict__) for item in items]

    async def get_item(self, id_param: UUID) -> ItemSchema:
        """Return a single item by its UUID.

        Args:
            id_param: The UUID of the item to retrieve.

        Returns:
            The matching ItemSchema.

        Raises:
            item_not_found_exception: When no item with the given UUID exists.

        """
        item = await self.repository.get_item(id_param)
        if item is None:
            raise item_not_found_exception
        return ItemSchema(**item.__dict__)

    async def get_user_items(self, owner: User) -> list[ItemSchema]:
        """Return all items belonging to a specific user.

        Args:
            owner: The authenticated user whose items to retrieve.

        Returns:
            A list of ItemSchema objects owned by the user.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the user owns no items.

        """
        items = await self.repository.get_user_items(owner)
        if not items:
            raise item_not_found_or_not_belong_to_user_exception
        return [ItemSchema(**item.__dict__) for item in items]

    async def get_user_item(self, item_id: UUID, owner: User) -> ItemSchema:
        """Return a specific item that belongs to a user.

        Args:
            item_id: The UUID of the item to retrieve.
            owner: The authenticated user who must own the item.

        Returns:
            The matching ItemSchema.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or is not owned by the user.

        """
        item = await self.repository.get_user_item(item_id, owner)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception
        return ItemSchema(**item.__dict__)

    async def create_item(self, item_data: ItemUpdateSchema, owner: User) -> ItemSchema:
        """Create a new item owned by a user.

        Args:
            item_data: Validated payload containing the item's field values.
            owner: The authenticated user who will own the item.

        Returns:
            The newly created ItemSchema.

        """
        item = await self.repository.create_item(item_data, owner)
        return ItemSchema(**item.__dict__)

    async def create_item_with_image(  # noqa: PLR0913, PLR0917
        self,
        name: str,
        description: str,
        price: float,
        tax: float,
        owner: User,
        image_file: UploadFile | None,
        caption: str,
    ) -> ItemSchema:
        """Create a new item and optionally attach an uploaded image.

        Checks that no other item shares the same name before creation.
        If an image file is supplied, it is saved to disk and its URL
        is stored on the new item record.

        Args:
            name: Display name for the item (must be unique).
            description: Human-readable description.
            price: Base price of the item.
            tax: Tax rate applied to the item.
            owner: The authenticated user who will own the item.
            image_file: Optional image file to attach to the item.
            caption: Alt-text or description for the image.

        Returns:
            The newly created ItemSchema, with ``image_url`` set when an
            image was provided.

        Raises:
            item_not_found_exception: Item not found.

        """
        existing = await self.repository.get_item_by_name(name)
        if existing is not None:
            raise item_not_found_exception

        item_data = ItemUpdateSchema(
            name=name, description=description, price=price, tax=tax
        )
        item = await self.repository.create_item(item_data, owner)

        if image_file:
            image = await save_image_file(image_file, caption)
            item = await self.repository.update_item_image(item.id, image.url)

        return ItemSchema(**item.__dict__)

    async def update_item(
        self, item_id: UUID, item_data: ItemUpdateSchema, owner: User | None = None
    ) -> ItemSchema:
        """Replace all fields of an item (PUT semantics).

        Every field is written, including those not explicitly set in the
        request (they receive their schema default values). When ``owner``
        is provided the update is scoped to items owned by that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Field values to write — all fields are applied.
            owner: If provided, restricts the update to items owned by this user.

        Returns:
            The updated ItemSchema.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the given owner.

        """
        item = await self.repository.update_item(item_id, item_data, owner)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception
        return ItemSchema(**item.__dict__)

    async def patch_item(
        self, item_id: UUID, item_data: ItemUpdateSchema, owner: User | None = None
    ) -> ItemSchema:
        """Apply a partial update to an item (PATCH semantics).

        Only fields explicitly provided in ``item_data`` are modified;
        omitted fields retain their current values. When ``owner`` is
        provided the update is scoped to items owned by that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Partial field values — only explicitly set fields are applied.
            owner: If provided, restricts the update to items owned by this user.

        Returns:
            The updated ItemSchema.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the given owner.

        """
        item = await self.repository.patch_item(item_id, item_data, owner)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception
        return ItemSchema(**item.__dict__)

    async def delete_item(self, item_id: UUID, owner: User) -> None:
        """Delete an item owned by the given user.

        Args:
            item_id: The UUID of the item to delete.
            owner: The authenticated user who must own the item.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the owner.

        """
        item = await self.repository.get_user_item(item_id, owner)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception
        await self.repository.delete_item(item)

    async def update_item_image(
        self, item_id: UUID, image_file: UploadFile, caption: str
    ) -> ItemSchema:
        """Save an uploaded image and associate it with an existing item.

        Args:
            item_id: The UUID of the item to attach the image to.
            image_file: The image file to persist to disk.
            caption: Alt-text or description stored alongside the image URL.

        Returns:
            The updated ItemSchema with the new ``image_url``.

        Raises:
            item_not_found_exception: When no item with the given UUID exists.

        """
        image = await save_image_file(image_file, caption)
        item = await self.repository.update_item_image(item_id, image.url)
        if item is None:
            raise item_not_found_exception
        return ItemSchema(**item.__dict__)
