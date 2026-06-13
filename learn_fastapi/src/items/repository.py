from typing import Any
from uuid import UUID

from sqlalchemy import and_, desc, select, update

from learn_fastapi.src.users.models import User
from learn_fastapi.src.utils.repository import BaseRepository, bool_to_column

from .models import Item
from .schema import ItemPatchSchema, ItemUpdateSchema


class ItemRepository(BaseRepository):
    """Repository class for Item ORM operations."""

    async def get_all_items(self) -> list[Item]:
        """Fetch every Item row from the database.

        Returns:
            A list of all Item ORM instances.

        """
        result = await self.session.execute(select(Item))
        return list(result.scalars().all())

    async def get_item(self, id_param: UUID) -> Item | None:
        """Fetch a single item by its primary-key UUID.

        Args:
            id_param: The UUID of the item to look up.

        Returns:
            The matching Item, or None if not found.

        """
        result = await self.session.execute(
            select(Item).where(bool_to_column(Item.id == id_param))
        )
        return result.scalar_one_or_none()

    async def get_item_by_name(self, name: str) -> Item | None:
        """Fetch a single item by its unique name.

        Args:
            name: The exact name to search for.

        Returns:
            The matching Item, or None if no item has that name.

        """
        result = await self.session.execute(select(Item).where(Item.name == name))
        return result.scalar_one_or_none()

    async def get_user_items(self, owner: User) -> list[Item]:
        """Fetch all items owned by a specific user.

        Args:
            owner: The user whose items to retrieve.

        Returns:
            A list of Item instances belonging to the user (may be empty).

        """
        result = await self.session.execute(
            select(Item).where(Item.user_id == owner.id).order_by(desc(Item.created_at))
        )
        return list(result.scalars().all())

    async def get_user_item(self, item_id: UUID, owner: User) -> Item | None:
        """Fetch a single item that belongs to a specific user.

        Args:
            item_id: The UUID of the item to look up.
            owner: The user who must own the item.

        Returns:
            The matching Item, or None if not found or not owned by the user.

        """
        condition = and_(bool_to_column(Item.id == item_id), Item.user_id == owner.id)
        result = await self.session.execute(select(Item).where(condition))
        return result.scalar_one_or_none()

    async def create_item(self, item_data: ItemUpdateSchema, owner: User) -> Item:
        """Persist a new item to the database.

        Args:
            item_data: Validated schema containing the item's field values.
            owner: The user who will own the new item.

        Returns:
            The freshly created and refreshed Item instance.

        """
        item = Item(
            **item_data.model_dump(exclude={"user_id"}), user_id=owner.id, user=owner
        )
        self.session.add(item)
        await self.commit()
        await self.session.refresh(item)
        return item

    def _superuser_management(
        self, item_id: UUID, owner: User | None
    ) -> tuple[Any, set[str] | None]:
        """Check if the user has permission to modify the item.

        Args:
            item_id: The UUID of the item to check permissions for.
            owner: The user attempting the operation, or None if unauthenticated.

        Returns:
            A tuple of (where_condition, exclude_args) where where_condition is a
            SQLAlchemy clause expression and exclude_args is a set of column names
            to exclude from updates, or None if no exclusions.

        """
        exclude_args = None
        if owner:
            condition = and_(
                bool_to_column(Item.id == item_id), Item.user_id == owner.id
            )
            exclude_args = {"user_id"}
        else:
            condition = Item.id == item_id
        return condition, exclude_args

    async def update_item(
        self, item_id: UUID, item_data: ItemUpdateSchema, owner: User | None = None
    ) -> Item | None:
        """Replace all fields of an item (PUT semantics).

        Applies every field from ``item_data``, including fields that were
        not explicitly set in the request (they receive their default values).
        If ``owner`` is provided, the update is scoped to items owned by
        that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Field values to write — all fields are applied.
            owner: If given, restricts the update to items owned by this user.
                Else the user is a superuser.

        Returns:
            The updated Item, or None if not found.

        """
        condition, exclude_args = self._superuser_management(item_id, owner)

        result = await self.session.execute(select(Item).where(condition))

        item = result.scalar_one_or_none()
        if item is None:
            return None

        values = item_data.model_dump(exclude=exclude_args, exclude_none=True)
        if "image_url" in values:
            values["image_public_id"] = None

        await self.session.execute(update(Item).where(condition).values(**values))
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def patch_item(
        self, item_id: UUID, item_data: ItemPatchSchema, owner: User | None = None
    ) -> Item | None:
        """Apply a partial update to an item (PATCH semantics).

        Only fields that were explicitly set in ``item_data`` are written;
        omitted fields retain their current database values.
        If ``owner`` is provided, the update is scoped to items owned by
        that user.

        Args:
            item_id: The UUID of the item to update.
            item_data: Partial field values — only explicitly set fields are applied.
            owner: If given, restricts the update to items owned by this user.

        Returns:
            The updated Item, or None if not found.

        """
        condition, exclude_args = self._superuser_management(item_id, owner)

        result = await self.session.execute(select(Item).where(condition))

        item = result.scalar_one_or_none()
        if item is None:
            return None

        values = item_data.model_dump(
            exclude=exclude_args, exclude_none=True, exclude_unset=True
        )
        if "image_url" in values:
            values["image_public_id"] = None

        await self.session.execute(update(Item).where(condition).values(**values))
        await self.commit()
        await self.session.refresh(item)
        return item

    async def update_item_image(
        self, item_id: UUID, image_url: str, image_public_id: str
    ) -> Item | None:
        """Update the Cloudinary image metadata of an item.

        Args:
            item_id: The UUID of the item to update.
            image_url: The new image URL to store on the item.
            image_public_id: The Cloudinary public ID for deletion/replacement.

        Returns:
            The updated Item.

        """
        id_bool_column = bool_to_column(Item.id == item_id)
        result = await self.session.execute(select(Item).where(id_bool_column))

        item = result.scalar_one_or_none()
        if item is None:
            return None

        await self.session.execute(
            update(Item)
            .where(id_bool_column)
            .values(image_url=image_url, image_public_id=image_public_id)
        )
        await self.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: Item) -> None:
        """Remove an item from the database.

        Args:
            item: The Item instance to delete.

        """
        await self.session.delete(item)
        await self.commit()
