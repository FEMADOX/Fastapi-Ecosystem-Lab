from dataclasses import dataclass

from fastapi import UploadFile

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
from learn_fastapi.src.items.application.use_cases import (
    CreateItemUseCase,
    CreateItemWithImageUseCase,
    DeleteItemUseCase,
    GetItemUseCase,
    GetOwnerItemUseCase,
    ListItemsUseCase,
    ListOwnerItemsUseCase,
    PatchItemUseCase,
    UpdateItemImageUseCase,
    UpdateItemUseCase,
)
from learn_fastapi.src.items.domain.entities import Item as ItemDomain
from learn_fastapi.src.items.domain.errors import (
    ItemDuplicatedNameError,
    ItemNotFoundError,
    ItemNotFoundForUserError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.infrastructure.mappers import (
    persisted_item_to_schema,
    persisted_item_with_image_to_schema,
    persisted_items_to_schema,
)
from learn_fastapi.src.items.presentation.exceptions import (
    duplicate_item_name_exception,
    item_not_found_exception,
    item_not_found_or_not_belong_to_user_exception,
)
from learn_fastapi.src.shared.application.dto import AuthenticatedAccount
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId
from learn_fastapi.src.shared.presentation.exceptions import user_doesnt_exist_exception
from learn_fastapi.src.users.application.queries import GetUserByIdQuery
from learn_fastapi.src.users.application.use_cases import GetUserByIdUseCase
from learn_fastapi.src.users.domain.errors import UserDoesntExistError
from learn_fastapi.src.users.models import User
from learn_fastapi.src.users.presentation.exceptions import (
    only_user_owner_is_authorized,
)
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
from .schema import ItemPatchSchema, ItemSchema, ItemUpdateSchema


@dataclass(frozen=True, slots=True)
class ItemsUseCases:
    """Application use cases required by ``ItemsService``."""

    get_user_by_id: GetUserByIdUseCase
    list_items: ListItemsUseCase
    get_item: GetItemUseCase
    list_owner_items: ListOwnerItemsUseCase
    get_owner_item: GetOwnerItemUseCase
    create_item: CreateItemUseCase
    update_item: UpdateItemUseCase
    patch_item: PatchItemUseCase
    delete_item: DeleteItemUseCase
    create_item_with_image: CreateItemWithImageUseCase
    update_item_image: UpdateItemImageUseCase


class ItemsService(BaseService):
    """Service class for Item business logic."""

    def __init__(self, use_cases: ItemsUseCases) -> None:
        """Initialize the service with an async database session."""
        self.use_cases = use_cases

    async def _resolve_owner(
        self, current_user: AuthenticatedAccount, owner_id: UserId | None
    ) -> User:
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
        if owner_id is None or owner_id == current_user.id:
            # Cache helpers still require the legacy ORM shape until items migrates.
            return User(
                id=current_user.id,
                email=current_user.email,
                password_hash=current_user.password_hash,
                is_active=current_user.is_active,
                is_superuser=current_user.is_superuser,
            )

        if not current_user.is_superuser:
            raise only_user_owner_is_authorized()

        try:
            owner = await self.use_cases.get_user_by_id.execute(
                GetUserByIdQuery(owner_id)
            )
            owner = User(
                id=owner.id,
                email=owner.email,
                password_hash=owner.password_hash,
                is_active=owner.is_active,
                is_superuser=owner.is_superuser,
            )
        except UserDoesntExistError as exc:
            raise user_doesnt_exist_exception() from exc
        return owner

    async def resolve_owner(
        self, current_user: AuthenticatedAccount, owner_id: UserId | None
    ) -> User:
        """Resolve the owner for user-scoped item reads."""  # noqa: DOC201
        return await self._resolve_owner(current_user, owner_id)

    @staticmethod
    def _item_from_update_schema(
        item_data: ItemUpdateSchema, owner_id: UserId | None
    ) -> ItemDomain:
        item_owner_id = item_data.user_id or owner_id
        if item_owner_id is None:
            msg = "owner_id is required to build an item domain entity"
            raise ValueError(msg)

        return ItemDomain(
            id=None,
            owner_id=item_owner_id,
            name=item_data.name,
            description=item_data.description or "No description provided",
            price=item_data.price,
            tax=item_data.tax,
            image_url=item_data.image_url or "",
        )

    async def list_all_items(self) -> list[ItemSchema]:
        """Return all items in the database as serialized schemas.

        Returns:
            A list of every ItemSchema (maybe empty).

        """
        cached = await get_cached_items()
        if cached:
            return [ItemSchema.model_validate(item) for item in cached]

        items = await self.use_cases.list_items.execute()
        schemas = persisted_items_to_schema(items)
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

        try:
            item = await self.use_cases.get_item.execute(GetItemQuery(id_param))
            schema = persisted_item_to_schema(item)
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

        try:
            items = await self.use_cases.list_owner_items.execute(
                ListOwnerItemsQuery(owner.id)
            )
            schemas = persisted_items_to_schema(items)
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
            item = await self.use_cases.get_owner_item.execute(
                GetOwnerItemQuery(item_id, owner.id)
            )
            schema = persisted_item_to_schema(item)
            await cache_user_item(item_id, schema.model_dump(mode="json"), owner)
        except ItemNotFoundForUserError as exception:
            raise item_not_found_or_not_belong_to_user_exception() from exception

        return schema

    async def create_item(
        self, item_data: ItemUpdateSchema, owner_id: UserId
    ) -> ItemSchema:
        """Create a new item owned by a user.

        Args:
            item_data: Validated payload containing the item's field values.
            owner_id: The authenticated user who will own the item.

        Returns:
            The newly created ItemSchema.

        """
        domain_item = self._item_from_update_schema(item_data, owner_id)
        item = await self.use_cases.create_item.execute(
            CreateItemCommand(domain_item, owner_id)
        )
        schema = persisted_item_to_schema(item)

        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
            item.owner_id,
        )

        return schema

    async def create_item_with_image(  # noqa: PLR0913, PLR0917
        self,
        name: str,
        description: str,
        price: float,
        tax: float,
        owner_id: UserId,
        image_file: UploadFile,
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
            owner_id: The authenticated user Id, who will own the item.
            image_file: Optional image file to attach to the item.
            caption: Alt-text or description for the image.

        Returns:
            The newly created ItemSchema, with ``image_url`` set when an
            image was provided.

        Raises:
            duplicate_item_name_exception: Item duplicated.

        """
        try:
            new_item = await self.use_cases.create_item_with_image.execute(
                CreateItemWithImageCommand(
                    owner_id, name, price, tax, image_file, caption, description
                )
            )
        except ItemDuplicatedNameError as exc:
            raise duplicate_item_name_exception() from exc

        schema = persisted_item_with_image_to_schema(new_item)

        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
        )
        await self._broadcast_sse_event(
            "item.created",
            schema.model_dump(mode="json"),
            new_item.owner_id,
        )

        return schema

    async def update_item(
        self,
        item_id: ItemId,
        item_data: ItemUpdateSchema,
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> ItemSchema:
        """Replace all fields of an item (PUT semantics).

        Every field is written, including those not explicitly set in the
        request (they receive their schema default values). When ``owner``
        is provided the update is scoped to items owned by that user.

        Args:
            item_id: The ItemId of the item to update.
            item_data: Field values to write — all fields are applied.
            owner_id: If provided, restricts the update to items owned by this user.
            is_superuser: Is the user modifier a superuser.

        Returns:
            The updated ItemSchema.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the given owner.

        """
        domain_item = self._item_from_update_schema(item_data, owner_id)
        try:
            item = await self.use_cases.update_item.execute(
                UpdateItemCommand(item_id, owner_id, is_superuser, domain_item)
            )
        except ItemNotFoundError as exc:
            raise item_not_found_or_not_belong_to_user_exception() from exc

        schema = persisted_item_to_schema(item)
        await self._broadcast_sse_event(
            "item.updated",
            schema.model_dump(mode="json"),
            user_id=item.owner_id,
        )

        return schema

    async def patch_item(
        self,
        item_id: ItemId,
        item_data: ItemPatchSchema,
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> ItemSchema:
        """Apply a partial update to an item (PATCH semantics).

        Only fields explicitly provided in ``item_data`` are modified;
        omitted fields retain their current values. When ``owner`` is
        provided the update is scoped to items owned by that user.

        Args:
            item_id: The ItemId of the item to update.
            item_data: Partial field values — only explicitly set fields are applied.
            owner_id: If provided, restricts the update to items owned by this user.
            is_superuser: Is the user modifier a superuser.

        Returns:
            The updated ItemSchema.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the given owner.

        """
        fields = item_data.model_dump(exclude_unset=True, exclude_none=True)
        try:
            item = await self.use_cases.patch_item.execute(
                PatchItemCommand(item_id, owner_id, is_superuser, fields)
            )
        except ItemNotFoundError as exc:
            raise item_not_found_or_not_belong_to_user_exception() from exc

        schema = persisted_item_to_schema(item)

        await self._broadcast_sse_event(
            "item.updated",
            schema.model_dump(mode="json"),
            user_id=item.owner_id,
        )

        return schema

    async def delete_item(self, item_id: ItemId, owner: AuthenticatedAccount) -> None:
        """Delete an item owned by the given user.

        Args:
            item_id: The ItemId of the item to delete.
            owner: The authenticated user who must own the item.

        Raises:
            item_not_found_or_not_belong_to_user_exception: When the item does not exist
                or does not belong to the owner.

        """
        try:
            item_deleted = await self.use_cases.delete_item.execute(
                DeleteItemCommand(item_id, owner.id, owner.is_superuser)
            )
        except ItemNotFoundError as exc:
            raise item_not_found_or_not_belong_to_user_exception() from exc

        schema = persisted_item_to_schema(item_deleted)
        await self._broadcast_sse_event(
            "item.deleted",
            schema.model_dump(mode="json"),
            user_id=item_deleted.owner_id,
        )

    async def update_item_image(
        self,
        item_id: ItemId,
        image_file: UploadFile,
        caption: str,
        owner: AuthenticatedAccount,
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
        try:
            item = await self.use_cases.update_item_image.execute(
                UpdateItemImageCommand(
                    item_id, owner.id, owner.is_superuser, image_file, caption
                )
            )
        except ItemNotFoundError as exc:
            raise item_not_found_or_not_belong_to_user_exception() from exc

        schema = persisted_item_with_image_to_schema(item)

        await self._broadcast_sse_event(
            "item.image_updated",
            schema.model_dump(mode="json"),
            user_id=item.owner_id,
        )

        return schema
