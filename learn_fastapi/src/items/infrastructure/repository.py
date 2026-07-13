from sqlalchemy import and_, desc, select

from learn_fastapi.src.items.domain.entities import Item as ItemDomain
from learn_fastapi.src.items.models import Item as ItemModel
from learn_fastapi.src.shared.domain.value_object import ItemId, UserId
from learn_fastapi.src.shared.infrastructure.repository import BaseSQLAlchemyRepository
from learn_fastapi.src.utils.repository import bool_to_column

from .mappers import item_from_orm, items_from_orm


class SQLAlchemyItemRepository(BaseSQLAlchemyRepository):
    """Repository for managing items using SQLAlchemy."""

    async def list_items(self) -> list[ItemDomain]:
        """List all items in the repository.

        Returns:
            A list of all items.

        """
        result = await self.session.execute(select(ItemModel))
        orm_items = list(result.scalars().all())
        return items_from_orm(orm_items)

    async def get_item_by_id(self, item_id: ItemId) -> ItemDomain | None:
        """Get an item by its ID.

        Args:
            item_id (ItemId): The ID of the item to retrieve.

        Returns:
            ItemDomain | None: The corresponding item, or None if not found.

        """
        result = await self.session.execute(
            select(ItemModel).where(bool_to_column(ItemModel.id == item_id))
        )
        orm_item = result.scalar_one_or_none()
        if not orm_item:
            return None
        return item_from_orm(orm_item)

    async def list_owner_items(self, owner_id: UserId) -> list[ItemDomain]:
        """List all items owned by a specific user.

        Args:
            owner_id (OwnerId): The ID of the owner whose items to retrieve.

        Returns:
            list[ItemDomain]: A list of items owned by the specified user.

        """
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.user_id == owner_id)
            .order_by(desc(ItemModel.created_at))
        )
        orm_items = list(result.scalars().all())
        return items_from_orm(orm_items)

    async def get_owner_item(
        self, item_id: ItemId, owner_id: UserId
    ) -> ItemDomain | None:
        """Get an owner item by its ID.

        Args:
            item_id (ItemId): The ID of the item to retrieve.
            owner_id (OwnerId): The ID of the owner whose item to retrieve.

        Returns:
            ItemDomain | None: The corresponding item, or None if not found.

        """
        condition = and_(
            bool_to_column(ItemModel.id == item_id), ItemModel.user_id == owner_id
        )
        result = await self.session.execute(select(ItemModel).where(condition))
        orm_item = result.scalar_one_or_none()
        if not orm_item:
            return None
        return item_from_orm(orm_item)
