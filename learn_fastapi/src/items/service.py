from fastapi import UploadFile

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.application.queries import (
    GetItemQuery,
    GetOwnerItemQuery,
    ListOwnerItemsQuery,
)
from learn_fastapi.src.items.application.use_cases import (
    GetItemUseCase,
    GetOwnerItemUseCase,
    ListItemsUseCase,
    ListOwnerItemsUseCase,
)
from learn_fastapi.src.items.domain.errors import (
    ItemNotFoundError,
    ItemNotFoundForUserError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.infrastructure.mappers import (
    item_domain_to_schema,
    items_domain_to_schema,
)
from learn_fastapi.src.items.infrastructure.repository import (
    SQLAlchemyItemRepository,
)
from learn_fastapi.src.items.presentation.exceptions import (
    duplicate_item_name_exception,
    item_not_found_exception,
    item_not_found_or_not_belong_to_user_exception,
)
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId
from learn_fastapi.src.shared.presentation.exceptions import user_doesnt_exist_exception
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.presentation.exceptions import (
    only_user_owner_is_authorized,
)
from learn_fastapi.src.users.repository import UsersRepository
from learn_fastapi.src.utils.service import BaseService

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
from .repository import ItemRepository
from .schema import ItemPatchSchema, ItemSchema, ItemUpdateSchema
from .utils import delete_image_file, save_image_file


class ItemService(BaseService):
    """Service class for Item business logic."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the service with an async database session."""
        self.repository = ItemRepository(session)
        self.users_repository = UsersRepository(session)

        clean_item_repository = SQLAlchemyItemRepository(session)
        self.list_item_use_case = ListItemsUseCase(clean_item_repository)
        self.get_item_use_case = GetItemUseCase(clean_item_repository)
        self.list_owner_items_use_case = ListOwnerItemsUseCase(clean_item_repository)
        self.get_owner_item_use_case = GetOwnerItemUseCase(clean_item_repository)

    async def _resolve_owner(self, current_user: User, owner_id: UserId | None) -> User:
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

    async def resolve_owner(self, current_user: User, owner_id: UserId | None) -> User:
        return await self._resolve_owner(current_user, owner_id)

    async def list_all_items(self) -> list[ItemSchema]:
        """Return all items in the database as serialized schemas.

        Returns:
            A list of every ItemSchema (maybe empty).

        """
        cached = await get_cached_items()
        if cached:
            return [ItemSchema.model_validate(item) for item in cached]

        items = await self.list_item_use_case.execute()
        schemas = items_domain_to_schema(items)
        await cache_items([schema.model_dump(mode="json") for schema in schemas])

        return schemas

    async def get_item(self, id_param: ItemId) -> ItemSchema:
        """Return a single item by its ItemId.

        Args:
            id_param: The ItemId of the item to retrieve.

        Returns:
            The matching ItemSchema.

        Raises:
            item_not_found_exception: When no item with the given ItemId exists.

        """
        cached = await get_cached_item(id_param)
        if cached:
            return ItemSchema.model_validate(cached)

        query = GetItemQuery(id_param)
        try:
            item = await self.get_item_use_case.execute(query)
            schema = item_domain_to_schema(item)
            await cache_item(id_param, schema.model_dump(mode="json"))

        except ItemNotFoundError as exception:
            raise item_not_found_exception() from exception

        return schema

    async def list_user_items(self, owner: User) -> list[ItemSchema]:
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

        query = ListOwnerItemsQuery(owner.id)
        try:
            items = await self.list_owner_items_use_case.execute(query)
            schemas = items_domain_to_schema(items)
            await cache_user_items(
                [schema.model_dump(mode="json") for schema in schemas], owner
            )

        except ItemsNotFoundForUserError as exception:
            raise item_not_found_or_not_belong_to_user_exception() from exception

        return schemas

    async def get_user_item(self, item_id: ItemId, owner: User) -> ItemSchema:
        """Return a specific item that belongs to a user.

        Args:
            item_id: The ItemId of the item to retrieve.
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

        try:
            query = GetOwnerItemQuery(item_id, owner.id)
            item = await self.get_owner_item_use_case.execute(query)
            schema = item_domain_to_schema(item)
            await cache_user_item(item_id, schema.model_dump(mode="json"), owner)
        except ItemNotFoundForUserError as exception:
            raise item_not_found_or_not_belong_to_user_exception() from exception

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

        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
            item.user_id,
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
        If an image file is supplied, it is uploaded and its URL
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
            await self.repository.update_item_image(item.id, image.url, image.public_id)

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
            item.user_id,
        )

        return schema

    async def update_item(
        self, item_id: ItemId, item_data: ItemUpdateSchema, owner: User | None = None
    ) -> ItemSchema:
        """Replace all fields of an item (PUT semantics).

        Every field is written, including those not explicitly set in the
        request (they receive their schema default values). When ``owner``
        is provided the update is scoped to items owned by that user.

        Args:
            item_id: The ItemId of the item to update.
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
        await self._broadcast_sse_event(
            "item.updated",
            schema.model_dump(mode="json"),
            user_id=item.user_id,
        )

        return schema

    async def patch_item(
        self, item_id: ItemId, item_data: ItemPatchSchema, owner: User | None = None
    ) -> ItemSchema:
        """Apply a partial update to an item (PATCH semantics).

        Only fields explicitly provided in ``item_data`` are modified;
        omitted fields retain their current values. When ``owner`` is
        provided the update is scoped to items owned by that user.

        Args:
            item_id: The ItemId of the item to update.
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

        await self._broadcast_sse_event(
            "item.updated",
            schema.model_dump(mode="json"),
            user_id=item.user_id,
        )

        return schema

    async def delete_item(self, item_id: ItemId, owner: User) -> None:
        """Delete an item owned by the given user.

        Args:
            item_id: The ItemId of the item to delete.
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
        await self._broadcast_sse_event(
            "item.deleted",
            schema.model_dump(mode="json"),
            user_id=item.user_id,
        )

    async def update_item_image(
        self,
        item_id: ItemId,
        image_file: UploadFile,
        caption: str,
        owner: User,
    ) -> ItemSchema:
        """Upload an image and associate it with an existing item.

        Args:
            item_id: The ItemId of the item to attach the image to.
            image_file: The image file to upload.
            caption: Alt-text or description stored alongside the image URL.
            owner: The authenticated user who must own the item.

        Returns:
            The updated ItemSchema with the new ``image_url``.

        Raises:
            item_not_found_or_not_belong_to_user_exception:
                When the item does not exist or does not belong to the owner.

        """
        if owner.is_superuser:
            item = await self.repository.get_item(item_id)
        else:
            item = await self.repository.get_user_item(item_id, owner)

        if item is None:
            raise item_not_found_or_not_belong_to_user_exception()

        if item.image_public_id:
            await delete_image_file(item.image_public_id)

        image = await save_image_file(image_file, caption)
        item = await self.repository.update_item_image(
            item.id,
            image.url,
            image.public_id,
        )

        if item is None:
            raise item_not_found_or_not_belong_to_user_exception()

        schema = ItemSchema.model_validate(item, from_attributes=True)

        await self._broadcast_sse_event(
            "item.image_updated",
            schema.model_dump(mode="json"),
            user_id=item.user_id,
        )

        return schema
