"""Fixtures for SSE tests."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
from httpx import AsyncClient
from starlette.status import HTTP_200_OK, HTTP_201_CREATED


@pytest.fixture
def test_item_data() -> dict[str, str | float]:
    """Test item data for SSE events.

    Returns:
        A dictionary representing an item, used as payload in SSE events.

    """
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Test Item",
        "description": "A test item",
        "price": 9.99,
        "tax": 0.99,
    }


@pytest.fixture
async def auth_client(client: AsyncClient) -> AsyncGenerator[AsyncClient]:
    """Client authenticated for SSE tests.

    Registers and logs in a test user, then returns a client with
    the Authorization header set.

    Yields:
        An authenticated AsyncClient instance.

    """
    # why: ensure each test run uses a unique account to avoid duplicate-user failures.
    email = f"sse_test_{uuid4()}@example.com"
    password = "sse_test_password"  # noqa: S105

    # Register a test user.
    register_response = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == HTTP_201_CREATED

    # Login to get token
    login_response = await client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == HTTP_200_OK

    token = login_response.json()["access_token"]

    # Set authorization header for all subsequent requests
    client.headers["Authorization"] = f"Bearer {token}"

    yield client

    # Cleanup: remove the authorization header
    client.headers.pop("Authorization", None)
