"""Server-Sent Events (SSE) manager for real-time notifications."""

import asyncio
import json
import logging
from uuid import UUID

logger = logging.getLogger(__name__)


# class SSEvent(TypedDict):
#     event: str
#     payload: dict


class SSEManager:
    """Manager for Server-Sent Events (SSE) connections.

    Maintains separate channels for:
    - Global broadcasts: all connected clients receive the event
    - Per-user broadcasts: only that user's connected clients receive the event

    Each connection is represented as an asyncio.Queue that receives event messages.
    """

    def __init__(self) -> None:
        """Initialize the SSEManager with empty subscriber lists."""
        self._global: list[asyncio.Queue[str]] = []
        self._users: dict[UUID, list[asyncio.Queue[str]]] = {}

    def build_event_message(self, event: str, payload: dict) -> str:
        """Build an SSE-formatted message string.

        SSE format requires:
        - data: <json>
        - Two newlines at the end

        Args:
            event: The name of the event (e.g., "item.created").
            payload: A dict containing the event data.

        Returns:
            An SSE-formatted message string ready to send to clients.

        """
        message_data = json.dumps({"event": event, "payload": payload}, default=str)
        # SSE format: "data: <json>\n\n"
        return f"data: {message_data}\n\n"

    def subscribe_global(self) -> asyncio.Queue[str]:
        """Subscribe to global events.

        Returns:
            A new asyncio.Queue that will receive all global events.

        """
        queue: asyncio.Queue[str] = asyncio.Queue()
        self._global.append(queue)
        logger.debug(f"[SSE] Global subscription created. Total: {len(self._global)}")
        return queue

    def subscribe_user(self, user_id: UUID) -> asyncio.Queue[str]:
        """Subscribe to events for a specific user.

        Args:
            user_id: The UUID of the user.

        Returns:
            A new asyncio.Queue that will receive events for this user.

        """
        queue: asyncio.Queue[str] = asyncio.Queue()
        if user_id not in self._users:
            self._users[user_id] = []
        self._users[user_id].append(queue)
        logger.debug(
            f"[SSE] User subscription created for {user_id}. "
            f"Total for user: {len(self._users[user_id])}"
        )
        return queue

    def unsubscribe_global(self, queue: asyncio.Queue[str]) -> None:
        """Unsubscribe from global events.

        Args:
            queue: The asyncio.Queue to remove.

        """
        if queue in self._global:
            self._global.remove(queue)
            logger.debug(
                f"[SSE] Global subscription removed. Total: {len(self._global)}"
            )

    def unsubscribe_user(self, user_id: UUID, queue: asyncio.Queue[str]) -> None:
        """Unsubscribe from events for a specific user.

        Args:
            user_id: The UUID of the user.
            queue: The asyncio.Queue to remove.

        """
        if user_id in self._users and queue in self._users[user_id]:
            self._users[user_id].remove(queue)
            # Clean up empty user channel
            if not self._users[user_id]:
                del self._users[user_id]
            logger.debug(
                f"[SSE] User subscription removed for {user_id}. "
                f"Total for user: {len(self._users.get(user_id, []))}"
            )

    async def broadcast_global(self, event: str, payload: dict) -> None:
        """Broadcast an event to all globally connected clients.

        Args:
            event: The event name (e.g., "item.created").
            payload: The event data dict.

        """
        try:
            message = self.build_event_message(event, payload)
            tasks = [queue.put(message) for queue in self._global]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.debug(f"[SSE] Broadcast global: {event} to {len(tasks)} clients")
        except Exception:
            logger.exception(f"[SSE] Error broadcasting global event: {event}")

    async def broadcast_user(self, user_id: UUID, event: str, payload: dict) -> None:
        """Broadcast an event to all clients connected for a specific user.

        Args:
            user_id: The UUID of the user to target.
            event: The event name (e.g., "item.updated").
            payload: The event data dict.

        """
        if user_id not in self._users:
            logger.debug(f"[SSE] No subscribers for user {user_id}")
            return

        try:
            message = self.build_event_message(event, payload)
            tasks = [queue.put(message) for queue in self._users[user_id]]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.debug(
                    f"[SSE] Broadcast user: {event} to {user_id} ({len(tasks)} clients)"
                )
        except Exception:
            logger.exception(
                f"[SSE] Error broadcasting user event: {event} to {user_id}"
            )


# Global singleton instance
sse_manager = SSEManager()
