"""Tests for SSE (Server-Sent Events) functionality."""

import json
from uuid import uuid4

import pytest
from starlette.status import HTTP_200_OK

from learn_fastapi.src.shared.application.dto import AuthenticatedAccount
from learn_fastapi.src.sse.manager import sse_manager
from learn_fastapi.src.sse.presentation.router import sse_global, sse_me
from learn_fastapi.src.users.domain.value_objects import PasswordHash

EXPECTED_TWO_CONNECTIONS = 2


class TestSSESubscription:
    """Test class for SSE subscription functionality."""

    @pytest.mark.asyncio
    async def test_sse_global_subscription(self) -> None:
        """Test global SSE subscription.

        Verifies that:
        - The handler returns HTTP 200.
        - The response content-type is text/event-stream.

        """
        current_user = AuthenticatedAccount(
            id=uuid4(),
            email=f"sse_global_{uuid4()}@example.com",
            password_hash=PasswordHash("not-used"),  # noqa: S106
            is_active=True,
            is_superuser=False,
        )
        response = await sse_global(current_user)
        assert response.status_code == HTTP_200_OK
        assert response.media_type == "text/event-stream"

    @pytest.mark.asyncio
    async def test_sse_user_subscription(self) -> None:
        """Test user-specific SSE subscription.

        Verifies that:
        - The handler returns HTTP 200.
        - The response content-type is text/event-stream.

        """
        current_user = AuthenticatedAccount(
            id=uuid4(),
            email=f"sse_user_{uuid4()}@example.com",
            password_hash=PasswordHash("not-used"),  # noqa: S106
            is_active=True,
            is_superuser=False,
        )
        response = await sse_me(current_user)
        assert response.status_code == HTTP_200_OK
        assert response.media_type == "text/event-stream"


class TestSSEBroadcast:
    """Test class for SSE event broadcasting functionality."""

    @pytest.mark.asyncio
    async def test_sse_event_broadcast(
        self,
        test_item_data: dict[str, str | float],
    ) -> None:
        """Test SSE event broadcasting.

        Verifies that:
        - Events can be broadcast to user-specific subscribers.
        - The SSE manager properly queues events.

        """
        # Use a specific UUID for testing
        user_id = uuid4()

        # Subscribe to user events
        user_queue = sse_manager.subscribe_user(user_id)

        # Broadcast an event
        await sse_manager.broadcast_user(user_id, "item.created", test_item_data)

        # Verify that the event was queued (without consuming it)
        assert not user_queue.empty()

        # Clean up
        sse_manager.unsubscribe_user(user_id, user_queue)

    @pytest.mark.asyncio
    async def test_sse_global_broadcast(
        self,
        test_item_data: dict[str, str | float],
    ) -> None:
        """Test SSE global event broadcasting.

        Verifies that:
        - Global events are broadcast to all subscribers.
        - Multiple subscribers receive the event.

        """
        # Subscribe multiple clients to global events
        queue1 = sse_manager.subscribe_global()
        queue2 = sse_manager.subscribe_global()

        # Broadcast a global event
        await sse_manager.broadcast_global("item.created", test_item_data)

        # Verify that both queues received the event
        assert not queue1.empty()
        assert not queue2.empty()

        # Clean up
        sse_manager.unsubscribe_global(queue1)
        sse_manager.unsubscribe_global(queue2)


class TestSSEConnectionCleanup:
    """Test class for SSE connection cleanup functionality."""

    @pytest.mark.asyncio
    async def test_sse_global_connection_cleanup(self) -> None:
        """Test that global SSE connections are cleaned up on unsubscribe.

        Verifies that:
        - Unsubscribing from global events removes the queue.
        - The global subscriber count decreases correctly.

        """
        # Record initial count
        initial_count = sse_manager.global_subscribers_count()

        # Subscribe to global events
        queue = sse_manager.subscribe_global()
        assert sse_manager.global_subscribers_count() == initial_count + 1

        # Unsubscribe
        sse_manager.unsubscribe_global(queue)
        assert sse_manager.global_subscribers_count() == initial_count

    @pytest.mark.asyncio
    async def test_sse_user_connection_cleanup(self) -> None:
        """Test that user SSE connections are cleaned up on unsubscribe.

        Verifies that:
        - Unsubscribing from user events removes the queue.
        - The user channel is deleted when empty.

        """
        user_id = uuid4()

        # Subscribe to user events
        queue = sse_manager.subscribe_user(user_id)
        assert sse_manager.has_user_subscribers(user_id)
        assert sse_manager.user_subscribers_count(user_id) == 1

        # Unsubscribe
        sse_manager.unsubscribe_user(user_id, queue)
        assert not sse_manager.has_user_subscribers(user_id)

    @pytest.mark.asyncio
    async def test_sse_user_multiple_connections_cleanup(self) -> None:
        """Test cleanup with multiple connections for the same user.

        Verifies that:
        - Multiple connections for the same user are tracked correctly.
        - Removing one connection doesn't remove others.
        - The user channel is only deleted when all connections are removed.

        """
        user_id = uuid4()

        # Subscribe multiple times
        queue1 = sse_manager.subscribe_user(user_id)
        queue2 = sse_manager.subscribe_user(user_id)
        assert sse_manager.user_subscribers_count(user_id) == EXPECTED_TWO_CONNECTIONS

        # Unsubscribe one
        sse_manager.unsubscribe_user(user_id, queue1)
        assert sse_manager.has_user_subscribers(user_id)
        assert sse_manager.user_subscribers_count(user_id) == 1

        # Unsubscribe the other
        sse_manager.unsubscribe_user(user_id, queue2)
        assert not sse_manager.has_user_subscribers(user_id)


class TestSSEMessageFormat:
    """Test class for SSE message formatting."""

    def test_sse_message_format(self, test_item_data: dict[str, str | float]) -> None:
        r"""Test SSE message formatting.

        Verifies that:
        - Messages follow the SSE format (data: <json>\\n\\n).
        - The JSON payload contains the correct event and data.

        """
        event = "item.created"
        payload = test_item_data

        message = sse_manager.build_event_message(event, payload)

        # Verify format
        assert message.startswith("data: ")
        assert message.endswith("\n\n")

        # Parse the JSON part
        json_str = message[len("data: ") : -2]  # Remove "data: " and "\n\n"
        parsed = json.loads(json_str)

        assert parsed["event"] == event
        assert parsed["payload"] == payload

    def test_sse_message_format_with_special_chars(self) -> None:
        """Test SSE message formatting with special characters.

        Verifies that:
        - Messages handle special characters in payload correctly.
        - JSON encoding handles Unicode characters properly.

        """
        event = "item.updated"
        payload = {
            "id": str(uuid4()),
            "name": "Producto con ñ y acentos",
            "description": "Descripción con caracteres especiales: @#$%",
        }

        message = sse_manager.build_event_message(event, payload)

        # Parse and verify
        json_str = message[len("data: ") : -2]
        parsed = json.loads(json_str)

        assert parsed["event"] == event
        assert parsed["payload"]["name"] == "Producto con ñ y acentos"
