"""v1 test configuration and shared fixtures."""

from typing import TYPE_CHECKING

import pytest

from learn_fastapi.tests.conftest import ClientContext

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from httpx import AsyncClient

TEST_API_PREFIX = "/v1"


@pytest.fixture
async def client(
    client_context_factory: Callable[..., ClientContext],
) -> AsyncGenerator[AsyncClient]:
    """Return a TestClient for v1 routes using the shared test session.

    Shadows the global ``client`` fixture for all tests in this package.
    Overrides ``get_session`` to use the in-memory test DB.

    Args:
        client_context_factory (Callable[..., TestClientContext]):
            Factory that creates a test client context.

    Yields:
        Configured AsyncClient instance.

    """
    async with client_context_factory(api_prefix=TEST_API_PREFIX) as async_client:
        yield async_client
