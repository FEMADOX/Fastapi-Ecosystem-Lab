from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.auth.models import User
from learn_fastapi.src.auth.utils import hash_password
from learn_fastapi.src.database import get_session
from learn_fastapi.src.items.models import Item
from learn_fastapi.src.main import app
from learn_fastapi.src.utils.dependencies import get_current_user


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
    test_session: AsyncSession, test_user: User
) -> AsyncGenerator[AsyncClient]:
    """Return a TestClient with both session and current-user overrides.

    Shadows the global ``client`` fixture for all tests in this package.
    Overrides ``get_session`` to use the in-memory test DB and
    ``get_current_user`` to inject ``test_user``, bypassing JWT auth.

    Args:
        test_session: The test database session (from global fixture).
        test_user: A pre-created user to act as the authenticated owner.

    Yields:
        Configured AsyncClient instance.

    """

    def override_get_async_session() -> Generator[AsyncSession]:
        yield test_session

    def override_get_user() -> User:
        return test_user

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_get_async_session
    app.dependency_overrides[get_current_user] = override_get_user

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver"
    ) as async_client:
        yield async_client

    app.dependency_overrides = previous


@pytest.fixture
def sample_item() -> dict:
    """Item payload for use in POST / PUT requests.

    Returns:
        dict: A dictionary representing a valid Item payload.

    """
    return {
        "name": "Test Item",
        "description": "A new test description",
        "price": 9.99,
        "tax": 1.0,
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
