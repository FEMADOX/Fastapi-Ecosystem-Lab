from learn_fastapi.src.shared.domain.value_object import UserId
from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.users.domain.entities import PersistedUser


class SSEAuthEventPublisher:
    """Public the user event using the SSE manager."""

    @staticmethod
    async def auth_registered(user: PersistedUser) -> None:
        # Auth publishes only its contract, without depending on users adapters.
        payload = {"user_id": str(user.id), "email": user.email}

        await sse_manager.broadcast_user(
            user.id,
            "auth.registered",
            payload,
        )

    @staticmethod
    async def auth_logged_in(user_id: UserId) -> None:
        payload = {"user_id": str(user_id)}

        await sse_manager.broadcast_user(
            user_id,
            "auth.logged_in",
            payload,
        )

    @staticmethod
    async def auth_logged_out(user_id: UserId) -> None:
        """Publish a user-scoped logout event."""
        payload = {"user_id": str(user_id)}

        await sse_manager.broadcast_user(
            user_id,
            "auth.logged_out",
            payload,
        )
