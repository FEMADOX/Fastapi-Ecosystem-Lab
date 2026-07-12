from dataclasses import dataclass
from datetime import datetime

from learn_fastapi.src.shared.domain.value_object import ItemId, RefreshTokenId, UserId


@dataclass(slots=True)
class User:
    """Domain entity representing an user."""

    id: UserId | None
    items_ids: list[ItemId]
    refresh_tokens_ids: list[RefreshTokenId]
    email: str
    password_hash: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_owner_of_item(self, item_id: ItemId) -> bool:
        """Check if the user is the owner of a specific item.

        Args:
            item_id (ItemId): The ID of the item to check ownership for.

        Returns:
            bool: True if the user is the owner of the item, False otherwise.

        """
        return item_id in self.items_ids

    def is_owner_of_refresh_token(self, refresh_token_id: ItemId) -> bool:
        """Check if the user is the owner of a specific refresh token.

        Args:
            refresh_token_id (ItemId): The ID of the refresh token to check ownership
                for.

        Returns:
            bool: True if the user is the owner of the refresh token, False otherwise.

        """
        return refresh_token_id in self.refresh_tokens_ids

    def has_same_identity_as(self, other_id: UserId) -> bool:
        """Check if the user has the same identity as another user.

        Args:
            other_id (UserId): The ID of the other user to compare with.

        Returns:
            bool: True if the user has the same identity as the other user, False
                otherwise.

        """
        return self.id == other_id


@dataclass(frozen=True, slots=True)
class AuthenticatedUser:
    """Domain entity representing an authenticated user."""

    id: UserId
    items_ids: list[ItemId]
    refresh_tokens_ids: list[RefreshTokenId]
    email: str
    password_hash: str
    is_active: bool
    is_superuser: bool
