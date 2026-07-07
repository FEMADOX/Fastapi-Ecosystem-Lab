from dataclasses import dataclass

from learn_fastapi.src.shared.domain.value_object import ItemId, UserId


@dataclass(slots=True, frozen=True)
class ListItemsQuery: ...


@dataclass(slots=True, frozen=True)
class GetItemQuery:
    """Query for retrieving an item by its ID."""

    item_id: ItemId


@dataclass(slots=True, frozen=True)
class ListOwnerItemsQuery:
    """Query for retrieving all items belonging to a specific owner."""

    owner_id: UserId


@dataclass(slots=True, frozen=True)
class GetOwnerItemQuery:
    """Query for retrieving a specific item belonging to a specific owner."""

    item_id: ItemId
    owner_id: UserId
