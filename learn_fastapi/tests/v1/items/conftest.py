from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from learn_fastapi.src.auth.utils import hash_password
from learn_fastapi.src.items.models import Item
from learn_fastapi.src.users.models import User
from learn_fastapi.src.utils.dependencies import get_current_user
from learn_fastapi.tests.v1.conftest import TEST_API_PREFIX

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlalchemy.ext.asyncio import AsyncSession

    from learn_fastapi.tests.conftest import ClientContext


@pytest.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user in the database for items tests.

    Args:
        test_session: The test database session (from global fixture).

    Returns:
        User: The persisted user instance.

    """
    user = User(
        email="itemtest@example.com",
        password_hash=hash_password("password123"),
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def client(
    client_context_factory: Callable[..., ClientContext],
    test_user: User,
) -> AsyncGenerator[AsyncClient]:
    """Return a TestClient for v1 routes using the shared test session.

    Shadows the global ``client`` fixture for all tests in this package.
    Overrides ``get_session`` to use the in-memory test DB.

    Args:
        client_context_factory: Factory that creates a test client context.
        test_user: A pre-created user to act as the authenticated owner.

    Yields:
        Configured AsyncClient instance.

    """
    async with client_context_factory(
        api_prefix=TEST_API_PREFIX,
        dependency_overrides={get_current_user: lambda: test_user},
    ) as async_client:
        yield async_client


@pytest.fixture
def sample_item(test_user: User) -> dict:
    """Item payload for use in POST / PUT requests.

    Returns:
        dict: A dictionary representing a valid Item payload.

    """
    return {
        "name": "Test Item",
        "description": "A new test description",
        "price": 9.99,
        "tax": 1.0,
        "user_id": str(test_user.id),
    }


@pytest.fixture
async def seeded_item(test_session: AsyncSession, test_user: User) -> Item:
    """Insert a single 'Foo' item into the test DB owned by test_user.

    Args:
        test_session: The test database session (from global fixture).
        test_user: The user who owns the item.

    Returns:
        ItemModel: The persisted ORM instance with its UUID.

    """
    item = Item(
        name="Foo",
        description="Seeded test item description",
        price=10.0,
        tax=1.0,
        user_id=test_user.id,
    )
    test_session.add(item)
    await test_session.commit()
    await test_session.refresh(item)
    return item
