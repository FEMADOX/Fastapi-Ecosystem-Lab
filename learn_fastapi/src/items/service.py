from uuid import UUID

from fastapi import UploadFile

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.users.exceptions import only_user_owner_is_authorized
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.repository import UsersRepository
from learn_fastapi.src.utils.exceptions import user_doesnt_exist_exception

from .cache import (
    cache_item,
    cache_items,
    cache_user_item,
    cache_user_items,
    get_cached_item,
    get_cached_items,
    get_cached_user_item,
    get_cached_user_items,
)
from .exceptions import (
    duplicate_item_name_exception,
    item_not_found_exception,
    item_not_found_or_not_belong_to_user_exception,
)
from .repository import ItemRepository
from .schema import ItemSchema, ItemUpdateSchema
from .utils import save_image_file


class ItemService:
    """Service class for Item business logic."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository: ItemRepository = ItemRepository(session)
        self.users_repository: UsersRepository = UsersRepository(session)

    async def _resolve_owner(self, current_user: User, owner_id: UUID | None) -> User:
        """Resolve the owner for user-scoped item reads.

        Non-admin users can only query their own items. Admin users can target
        another account via ``owner_id``.

        Args:
            current_user: The authenticated user making the request.
            owner_id: Optional owner UUID. Only superusers can target another owner.

        Returns:
            The effective owner User object for the query.

        Raises:
            only_user_owner_is_authorized:
                When a non-superuser attempts to target another owner.
            user_doesnt_exist_exception: When the specified owner does not exist.

        """
        if not owner_id or owner_id == current_user.id:
            return current_user

        if not current_user.is_superuser:
            raise only_user_owner_is_authorized()

        owner = await self.users_repository.get_user_by_id(owner_id)
        if owner is None:
            raise user_doesnt_exist_exception()
        return owner

    async def resolve_owner(self, current_user: User, owner_id: UUID | None) -> User:
        return await self._resolve_owner(current_user, owner_id)

    async def get_all_items(self) -> list[ItemSchema]:
        """Return all items in the database as serialized schemas.

        Returns:
            A list of every ItemSchema (maybe empty).

        """
        cached = await get_cached_items()
        if cached:
            return [ItemSchema.model_validate(item) for item in cached]

        items = await self.repository.get_all_items()
        schemas = [
            ItemSchema.model_validate(item, from_attributes=True) for item in items
        ]

        await cache_items([schema.model_dump(mode="json") for schema in schemas])

        return schemas

    async def get_item(self, id_param: UUID) -> ItemSchema:
        """Return a single item by its UUID.

        Args:
            id_param: The UUID of the item to retrieve.

        Returns:
            The matching ItemSchema.

        Raises:
            item_not_found_exception: When no item with the given UUID exists.

        """
        cached = await get_cached_item(id_param)
        if cached:
            return ItemSchema.model_validate(cached)

        item = await self.repository.get_item(id_param)
        if item is None:
            raise item_not_found_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await cache_item(id_param, schema.model_dump(mode="json"))

        return schema

    async def get_user_items(self, owner: User) -> list[ItemSchema]:
        """Return all items belonging to a specific user.

        Args:
            owner: The authenticated user whose items to retrieve.

        Returns:
            A list of ItemSchema objects owned by the user.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the user owns no items.

        """
        cached = await get_cached_user_items(owner)
        if cached:
            return [ItemSchema.model_validate(item) for item in cached]

        items = await self.repository.get_user_items(owner)
        if not items:
            raise item_not_found_or_not_belong_to_user_exception()

        schemas = [
            ItemSchema.model_validate(item, from_attributes=True) for item in items
        ]

        await cache_user_items(
            [schema.model_dump(mode="json") for schema in schemas], owner
        )

        return schemas

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
        cached = await get_cached_user_item(item_id, owner)
        if cached:
            return ItemSchema.model_validate(cached)

        item = await self.repository.get_user_item(item_id, owner)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await cache_user_item(item_id, schema.model_dump(mode="json"), owner)

        return schema

    async def create_item(self, item_data: ItemUpdateSchema, owner: User) -> ItemSchema:
        """Create a new item owned by a user.

        Args:
            item_data: Validated payload containing the item's field values.
            owner: The authenticated user who will own the item.

        Returns:
            The newly created ItemSchema.

        """
        item = await self.repository.create_item(item_data, owner)
        schema = ItemSchema.model_validate(item, from_attributes=True)

        await sse_manager.broadcast_global(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await sse_manager.broadcast_user(
            owner.id,
            "item.created",
            schema.model_dump(mode="json"),
        )

        return schema

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
            duplicate_item_name_exception: Item duplicated.

        """
        existing = await self.repository.get_item_by_name(name)
        if existing:
            raise duplicate_item_name_exception()

        item_data = ItemUpdateSchema(
            name=name, description=description, price=price, tax=tax
        )
        item = await self.repository.create_item(item_data, owner)

        if image_file:
            image = await save_image_file(image_file, caption)
            item = await self.repository.update_item_image(item.id, image.url)

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await sse_manager.broadcast_global(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await sse_manager.broadcast_user(
            owner.id,
            "item.created",
            schema.model_dump(mode="json"),
        )

        return schema

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
        owner_scope = None if owner and owner.is_superuser else owner
        item = await self.repository.update_item(item_id, item_data, owner_scope)
        if not item:
            raise item_not_found_or_not_belong_to_user_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)
        await sse_manager.broadcast_user(
            item.user_id,  # ty:ignore[invalid-argument-type]
            "item.updated",
            schema.model_dump(mode="json"),
        )

        return schema

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
        owner_scope = None if owner and owner.is_superuser else owner
        item = await self.repository.patch_item(item_id, item_data, owner_scope)
        if item is None:
            raise item_not_found_or_not_belong_to_user_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await sse_manager.broadcast_user(
            item.user_id,  # ty:ignore[invalid-argument-type]
            "item.updated",
            schema.model_dump(mode="json"),
        )

        return schema

    async def delete_item(self, item_id: UUID, owner: User) -> None:
        """Delete an item owned by the given user.

        Args:
            item_id: The UUID of the item to delete.
            owner: The authenticated user who must own the item.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the owner.

        """
        if owner.is_superuser:
            item = await self.repository.get_item(item_id)
        else:
            item = await self.repository.get_user_item(item_id, owner)

        if item is None:
            raise item_not_found_or_not_belong_to_user_exception()

        await self.repository.delete_item(item)

        schema = ItemSchema.model_validate(item, from_attributes=True)
        await sse_manager.broadcast_user(
            owner.id,
            "item.deleted",
            schema.model_dump(mode="json"),
        )

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
            raise item_not_found_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await sse_manager.broadcast_user(
            item.user_id,  # ty:ignore[invalid-argument-type]
            "item.image_updated",
            schema.model_dump(mode="json"),
        )

        return schema
