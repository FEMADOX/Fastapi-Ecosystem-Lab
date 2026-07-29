"""SSE (Server-Sent Events) endpoints for real-time notifications."""

import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi_versionizer.versionizer import api_version

from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.utils.alembic import app_logger as logger

router = APIRouter(prefix="/events", tags=["events"])


async def _queue_messages(queue: asyncio.Queue) -> AsyncGenerator[str]:
    """Yield queued SSE messages and periodic keep-alive frames.

    Yields:
        SSE messages from the event generator.

    """
    while True:
        try:
            yield await asyncio.wait_for(queue.get(), timeout=30.0)
        except TimeoutError:
            # Keep the connection alive while the queue has no new events.
            yield ": keep-alive\n\n"


async def event_generator(
    queue: asyncio.Queue,
) -> AsyncGenerator[str]:
    """Yield SSE messages from a queue.

    Yields messages until the client disconnects or an error occurs.

    Args:
        queue: The asyncio.Queue to read messages from.

    Yields:
        SSE-formatted message strings.

    Raises:
        CancelledError: If the client disconnects.

    """
    try:
        yield ": connected\n\n"
        async for message in _queue_messages(queue):
            yield message
    except asyncio.CancelledError:
        logger.debug("[SSE] Client disconnected from event stream")
        raise
    except Exception:
        logger.exception("[SSE] Error in event generator")
        raise


@api_version(1)
@router.get("/global")
async def sse_global(current_user: CurrentUserDep) -> StreamingResponse:
    """Stream global events to the authenticated client.

    Global events are sent to all connected clients\
        (e.g., when any user creates an item).

    Args:
        current_user: The authenticated user (for access control).

    Returns:
        A StreamingResponse that sends SSE events to the client.

    """
    queue = sse_manager.subscribe_global()
    logger.debug(f"[SSE] User {current_user.id} subscribed to global events")

    async def cleanup_generator() -> AsyncGenerator[str]:
        """Handle subscription cleanup on disconnect.

        Yields:
            SSE messages from the event generator.

        """
        try:
            async for message in event_generator(queue):
                yield message
        finally:
            sse_manager.unsubscribe_global(queue)
            logger.debug(
                f"[SSE] User {current_user.id} unsubscribed from global events"
            )

    return StreamingResponse(
        cleanup_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@api_version(1)
@router.get("/me")
async def sse_me(current_user: CurrentUserDep) -> StreamingResponse:
    """Stream user-scoped events to the authenticated client.

    User-scoped events are sent only to that user's connected clients\
        (e.g., when their item is updated).

    Args:
        current_user: The authenticated user who will receive their events.

    Returns:
        A StreamingResponse that sends SSE events to the client.

    """
    queue = sse_manager.subscribe_user(current_user.id)
    logger.debug(f"[SSE] User {current_user.id} subscribed to their user events")

    async def cleanup_generator() -> AsyncGenerator[str]:
        """Handle subscription cleanup on disconnect.

        Yields:
            SSE messages from the event generator.

        """
        try:
            async for message in event_generator(queue):
                yield message
        finally:
            sse_manager.unsubscribe_user(current_user.id, queue)
            logger.debug(f"[SSE] User {current_user.id} unsubscribed from their events")

    return StreamingResponse(
        cleanup_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
