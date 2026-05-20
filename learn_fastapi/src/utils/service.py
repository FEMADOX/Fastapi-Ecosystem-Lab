"""Base service class with shared SSE broadcasting utilities."""

from uuid import UUID

from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.utils.alembic import app_logger


class BaseService:
    """Base class for all service layers.

    Provides a shared ``_broadcast_sse_event`` helper so every subclass can
    emit SSE events without duplicating the try/except guard and logging.
    """

    @staticmethod
    async def _broadcast_sse_event(
        event: str, payload: dict, user_id: UUID | None = None
    ) -> None:
        """Safely broadcast an SSE event, logging failures without raising.

        Wraps SSE broadcast calls to ensure failures don't interrupt business
        logic. This is a best-effort approach: if SSE is unavailable or fails,
        the API continues normally.

        Args:
            event: Event type (e.g., ``"item.created"``).
            payload: Event payload dict.
            user_id: Optional user ID for user-scoped events. When ``None``
                the event is broadcast globally to all connected clients.

        """
        try:
            if user_id:
                await sse_manager.broadcast_user(user_id, event, payload)
            else:
                await sse_manager.broadcast_global(event, payload)
        except Exception:  # noqa: BLE001
            app_logger.exception(
                f"Failed to broadcast SSE event '{event}' (user_id={user_id})"
            )
