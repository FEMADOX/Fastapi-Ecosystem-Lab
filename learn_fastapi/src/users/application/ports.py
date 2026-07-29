from typing import Protocol

from learn_fastapi.src.users.domain.entities import PersistedUser


class UsersEventPublisher(Protocol):
    """Protocol for sse in the item operations."""

    async def account_updated(
        self, user: PersistedUser, changed_fields: list[str]
    ) -> None: ...
    async def account_deleted(self, user: PersistedUser) -> None: ...
