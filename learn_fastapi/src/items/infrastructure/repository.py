from sqlalchemy import and_, desc, select, update
from sqlalchemy.sql.elements import ColumnElement

from learn_fastapi.src.items.domain.entities import (
    Item as ItemDomain,
)
from learn_fastapi.src.items.domain.entities import (
    ItemImage,
    PersistedItem,
    PersistedItemWithImage,
)
from learn_fastapi.src.items.models import Item as ItemModel
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId
from learn_fastapi.src.shared.infrastructure.repository import BaseSQLAlchemyRepository
from learn_fastapi.src.utils.repository import bool_to_column

from .mappers import (
    persisted_item_from_orm,
    persisted_item_with_image_from_orm,
    persisted_items_from_orm,
)


class SQLAlchemyItemsRepository(BaseSQLAlchemyRepository):
    """Repository for managing items using SQLAlchemy."""

    async def _get_item_by_id(
        self, item_id: ItemId, owner_id: UserId | None = None
    ) -> ItemModel | None:
        """Get an item by its ID.

        Args:
            item_id (ItemId): The ID of the item to retrieve.
            owner_id (UserId): The item owner ID.

        Returns:
            The corresponding item, or None if not found.

        """
        statement = select(ItemModel).where(bool_to_column(ItemModel.id == item_id))
        if owner_id:
            statement = statement.where(ItemModel.user_id == owner_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_items(self) -> list[PersistedItem]:
        """List all items in the repository.

        Returns:
            A list of all items.

        """
        result = await self.session.execute(select(ItemModel))
        orm_items = list(result.scalars().all())
        return persisted_items_from_orm(orm_items)

    async def get_item_by_id(self, item_id: ItemId) -> PersistedItem | None:
        """Get an item by its ID.

        Args:
            item_id (ItemId): The ID of the item to retrieve.

        Returns:
            The corresponding item, or None if not found.

        """
        orm_item = await self._get_item_by_id(item_id)
        if not orm_item:
            return None
        return persisted_item_from_orm(orm_item)

    async def get_item_by_name(self, item_name: str) -> PersistedItem | None:
        """Get an item by its name.

        Args:
            item_name: The name of the item to retrieve.

        Returns:
            The corresponding item, or None if not found.

        """
        statement = select(ItemModel).where(ItemModel.name == item_name)
        result = await self.session.execute(statement)
        orm_item = result.scalar_one_or_none()
        if orm_item is None:
            return None
        return persisted_item_from_orm(orm_item)

    async def list_owner_items(self, owner_id: UserId) -> list[PersistedItem]:
        """List all items owned by a specific user.

        Args:
            owner_id (OwnerId): The ID of the owner whose items to retrieve.

        Returns:
            A list of items owned by the specified user.

        """
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.user_id == owner_id)
            .order_by(desc(ItemModel.created_at))
        )
        orm_items = list(result.scalars().all())
        return persisted_items_from_orm(orm_items)

    async def get_owner_item(
        self, item_id: ItemId, owner_id: UserId
    ) -> PersistedItem | None:
        """Get an owner item by its ID.

        Args:
            item_id (ItemId): The ID of the item to retrieve.
            owner_id (OwnerId): The ID of the owner whose item to retrieve.

        Returns:
            The corresponding item, or None if not found.

        """
        condition = and_(
            bool_to_column(ItemModel.id == item_id), ItemModel.user_id == owner_id
        )
        result = await self.session.execute(select(ItemModel).where(condition))
        orm_item = result.scalar_one_or_none()
        if not orm_item:
            return None
        return persisted_item_from_orm(orm_item)

    async def create_item(
        self, owner_id: UserId, item_data: ItemDomain
    ) -> PersistedItem:
        """Create a new item owned by a user.

        Args:
            item_data: Validated payload containing the item's field values.
            owner_id: The owner id.

        Returns:
            The newly created ItemSchema.

        """
        orm_item = ItemModel(
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            tax=item_data.tax,
            image_url=item_data.image_url,
            image_public_id=item_data.image_public_id,
            user_id=owner_id,
        )
        self.session.add(orm_item)
        await self.commit()
        await self.session.refresh(orm_item)
        return persisted_item_from_orm(orm_item)

    @staticmethod
    def _superuser_management(
        item_id: ItemId, owner_id: UserId | None, is_superuser: bool | None
    ) -> tuple[ColumnElement[bool], set[str] | None]:
        """Build the SQLAlchemy condition for owner-scoped item writes.

        Args:
            item_id: The item id to check permissions for.
            owner_id: The user attempting the operation, or None for superusers.
            is_superuser: Is the user modifier a superuser.

        Returns:
            A tuple of (where_condition, exclude_args) where where_condition is a
            SQLAlchemy clause expression and exclude_args is a set of column names
            to exclude from updates, or None if no exclusions.

        """
        exclude_args = None
        condition = bool_to_column(False)  # noqa: FBT003
        if is_superuser:
            condition = bool_to_column(ItemModel.id == item_id)
            return condition, exclude_args
        if owner_id:
            condition = and_(
                bool_to_column(ItemModel.id == item_id),
                ItemModel.user_id == owner_id,
            )
            exclude_args = {"user_id"}
        return condition, exclude_args

    async def update_item(
        self,
        item_id: ItemId,
        item_data: ItemDomain,
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> PersistedItem | None:
        """Replace all fields of an item (PUT semantics).

        Applies every field from ``item_data``, including fields that were
        not explicitly set in the request (they receive their default values).
        If ``owner`` is provided, the update is scoped to items owned by
        that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Field values to write; all fields are applied.
            owner_id: If given, restricts the update to items owned by this user.
                Else the user is a superuser.
            is_superuser: Is the user modifier a superuser.

        Returns:
            The updated Item, or None if not found.

        """
        condition, excluded_arg = self._superuser_management(
            item_id, owner_id, is_superuser
        )

        result = await self.session.execute(select(ItemModel).where(condition))

        orm_item = result.scalar_one_or_none()
        if orm_item is None:
            return None

        values_to_update = {
            "name": item_data.name,
            "description": item_data.description,
            "price": item_data.price,
            "tax": item_data.tax,
            "image_url": item_data.image_url,
            "image_public_id": item_data.image_public_id,
            "user_id": item_data.owner_id,
        }
        if excluded_arg:
            for field in excluded_arg:
                values_to_update.pop(field, None)
        if item_data.image_url:
            values_to_update["image_public_id"] = None

        await self.session.execute(
            update(ItemModel).where(condition).values(**values_to_update)
        )
        await self.commit()
        await self.session.refresh(orm_item)
        return persisted_item_from_orm(orm_item)

    async def patch_item(
        self,
        item_id: ItemId,
        item_data: dict[str, object],
        is_superuser: bool,
        owner_id: UserId | None = None,
    ) -> PersistedItem | None:
        """Apply a partial update to an item (PATCH semantics).

        Only fields that were explicitly set in ``item_data`` are written;
        omitted fields retain their current database values.
        If ``owner`` is provided, the update is scoped to items owned by
        that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Partial field values — only explicitly set fields are applied.
            owner_id: If given, restricts the update to items owned by this user.
            is_superuser: Is the user modifier a superuser.

        Returns:
            The patched Item, or None if not found.

        """
        condition, excluded_arg = self._superuser_management(
            item_id, owner_id, is_superuser
        )

        result = await self.session.execute(select(ItemModel).where(condition))

        orm_item = result.scalar_one_or_none()
        if orm_item is None:
            return None

        values_to_update = dict(item_data)
        if excluded_arg:
            for field in excluded_arg:
                values_to_update.pop(field, None)
        if "image_url" in values_to_update:
            values_to_update["image_public_id"] = None

        await self.session.execute(
            update(ItemModel).where(condition).values(**values_to_update)
        )
        await self.commit()
        await self.session.refresh(orm_item)
        return persisted_item_from_orm(orm_item)

    async def delete_item(
        self, item_id: ItemId, owner_id: UserId | None = None
    ) -> PersistedItem | None:
        """Remove an item from the database.

        Args:
            item_id: The Item id to delete.
            owner_id: The item owner ID.

        Returns:
            Persisted Item or None if not found.

        """
        orm_item = await self._get_item_by_id(item_id, owner_id)
        if orm_item is None:
            return None

        await self.session.delete(orm_item)
        await self.commit()
        return persisted_item_from_orm(orm_item)

    async def create_item_with_image(  # noqa: PLR0913, PLR0917
        self,
        owner_id: UserId,
        name: str,
        description: str,
        price: float,
        tax: float,
        image: ItemImage,
    ) -> PersistedItemWithImage:
        orm_item = ItemModel(
            name=name,
            description=description,
            price=price,
            tax=tax,
            image_url=image.url,
            image_public_id=image.public_id,
            user_id=owner_id,
        )
        self.session.add(orm_item)
        await self.session.commit()
        await self.session.refresh(orm_item)
        return persisted_item_with_image_from_orm(orm_item)

    async def update_item_with_image(
        self,
        item_id: ItemId,
        owner_id: UserId | None,
        image: ItemImage,
    ) -> PersistedItemWithImage | None:
        """Update the Cloudinary image metadata of an item.

        Args:
            item_id: The ID of the item to update.
            owner_id: The owner ID of the item.
            image: The Cloudinary public ID for deletion/replacement.

        Returns:
            The updated Item.

        """
        orm_item = await self._get_item_by_id(item_id, owner_id)
        if orm_item is None:
            return None

        await self.session.execute(
            update(ItemModel)
            .where(bool_to_column(ItemModel.id == item_id))
            .values(image_url=image.url, image_public_id=image.public_id)
        )
        await self.commit()
        await self.session.refresh(orm_item)
        return persisted_item_with_image_from_orm(orm_item)
