from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.users.domain.entities import PersistedUser


class SSEUsersEventPublisher:
    """Public the user event using the SSE manager."""

    @staticmethod
    async def account_updated(user: PersistedUser, changed_fields: list[str]) -> None:
        await sse_manager.broadcast_user(
            user.id,
            "user.account_updated",
            {
                "user_id": str(user.id),
                "changed_fields": changed_fields,
            },
        )

    @staticmethod
    async def account_deleted(user: PersistedUser) -> None:
        await sse_manager.broadcast_user(
            user.id,
            "user.account_deleted",
            {"user_id": str(user.id)},
        )
