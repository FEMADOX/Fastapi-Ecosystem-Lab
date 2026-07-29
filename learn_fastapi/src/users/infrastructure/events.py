from pydantic import BaseModel

from learn_fastapi.src.shared.domain.value_object import ItemId, RefreshTokenId, UserId
from learn_fastapi.src.shared.infrastructure.json_types import (
    model_dump_json_object,
)
from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.users.domain.entities import PersistedUser


class UsersEventRecord(BaseModel):
    """Public payload sent from SSE for a user."""

    id: UserId
    items_ids: list[ItemId]
    refresh_tokens_ids: list[RefreshTokenId]
    email: str
    is_active: bool
    is_superuser: bool

    @classmethod
    def from_domain(cls, user: PersistedUser) -> UsersEventRecord:
        return cls(
            id=user.id,
            items_ids=user.items_ids,
            refresh_tokens_ids=user.refresh_tokens_ids,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )


class SSEUsersEventPublisher:
    """Public the user event using the SSE manager."""

    @staticmethod
    async def account_updated(user: PersistedUser, changed_fields: list[str]) -> None:
        user_id = model_dump_json_object(
            UsersEventRecord.from_domain(user), include={"id"}
        )
        payload = {"user_id": user_id, "changed_fields": changed_fields}

        await sse_manager.broadcast_user(
            user.id,
            "user.account_updated",
            payload,
        )

    @staticmethod
    async def account_deleted(user: PersistedUser) -> None:
        user_id = model_dump_json_object(
            UsersEventRecord.from_domain(user), include={"id"}
        )
        payload = {"user_id": user_id}

        await sse_manager.broadcast_user(
            user.id,
            "user.account_deleted",
            payload,
        )
