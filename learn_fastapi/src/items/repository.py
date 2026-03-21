from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import and_, select, update

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.models import Item
from learn_fastapi.src.items.schema import ItemUpdateSchema
from learn_fastapi.src.users.models import User

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio.session import AsyncSession


class ItemRepository:
    """Repository class for Item ORM operations."""

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the repository with an async database session."""
        self.session: AsyncSession = session

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()

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
        result = await self.session.execute(select(Item).where(Item.id == id_param))
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
            select(Item).where(Item.user_id == owner.id)
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
        condition = and_(Item.id == item_id, Item.user_id == owner.id)
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
    ) -> tuple[and_, set[str] | None]:
        """Check if the user has permission to modify the item.

        Args:
            item_id: The UUID of the item to check permissions for.
            owner: The user attempting the operation, or None if unauthenticated.

        Returns:
            True if the user has permission to modify the item, False otherwise.

        """
        exclude_args = None
        if owner:
            condition = and_(Item.id == item_id, Item.user_id == owner.id)
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

        await self.session.execute(
            update(Item)
            .where(condition)
            .values(**item_data.model_dump(exclude=exclude_args))
        )
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def patch_item(
        self, item_id: UUID, item_data: ItemUpdateSchema, owner: User | None = None
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

        await self.session.execute(
            update(Item)
            .where(condition)
            .values(**item_data.model_dump(exclude=exclude_args, exclude_unset=True))
        )
        await self.commit()
        await self.session.refresh(item)
        return item

    async def update_item_image(self, item_id: UUID, image_url: str) -> Item | None:
        """Update the image_url of an item.

        Args:
            item_id: The UUID of the item to update.
            image_url: The new image URL to store on the item.

        Returns:
            The updated Item.

        """
        result = await self.session.execute(select(Item).where(Item.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            return None

        await self.session.execute(
            update(Item).where(Item.id == item_id).values(image_url=image_url)
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
