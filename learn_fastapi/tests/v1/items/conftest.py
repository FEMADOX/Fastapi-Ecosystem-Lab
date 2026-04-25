from typing import TYPE_CHECKING
from uuid import UUID

import fakeredis
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from learn_fastapi.src.auth.utils import hash_password
from learn_fastapi.src.cache import redis_client as redis_client_module
from learn_fastapi.src.items.models import Item
from learn_fastapi.src.users.models import User
from learn_fastapi.src.utils.dependencies import get_current_user
from learn_fastapi.tests.v1.conftest import TEST_API_PREFIX
from learn_fastapi.tests.v1.items.test_items_authorization import register_and_login

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlalchemy.ext.asyncio import AsyncSession

    from learn_fastapi.tests.conftest import ClientContext


@pytest.fixture(autouse=True)
async def fake_redis(monkeypatch: pytest.MonkeyPatch) -> AsyncGenerator:
    """Replace the global Redis client with an in-process fakeredis instance.

    ``autouse=True`` ensures every test in this package runs against a clean,
    isolated fake Redis — no real Redis server is required.
    """
    fake = fakeredis.aioredis.FakeRedis(decode_responses=False)
    monkeypatch.setattr(redis_client_module, "_redis_client", fake)
    yield
    await fake.aclose()


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
async def auth_client(
    client_context_factory: Callable[..., ClientContext],
) -> AsyncGenerator[AsyncClient]:
    """Return a v1 client that uses the real authentication dependencies."""
    async with client_context_factory(api_prefix=TEST_API_PREFIX) as async_client:
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


@pytest.fixture
async def owner_token(auth_client: AsyncClient) -> str:
    return await register_and_login(
        auth_client,
        email="owner@example.com",
        password="owner_password_123",  # noqa: S106
    )


@pytest.fixture
async def other_user_token(auth_client: AsyncClient) -> str:
    return await register_and_login(
        auth_client,
        email="other@example.com",
        password="other_password_123",  # noqa: S106
    )


@pytest.fixture
async def admin_token(auth_client: AsyncClient, test_session: AsyncSession) -> str:
    email = "admin@example.com"
    token = await register_and_login(
        auth_client,
        email=email,
        password="admin_password_123",  # noqa: S106
    )

    result = await test_session.execute(select(User).where(User.email == email))
    admin_user = result.scalar_one()
    admin_user.is_superuser = True
    await test_session.commit()

    return token


@pytest.fixture
async def owner_item_id(auth_client: AsyncClient, owner_token: str) -> UUID:
    response = await auth_client.post(
        "/items/",
        json={
            "name": "Owner Item",
            "description": "Owned by owner",
            "price": 10.0,
            "tax": 1.0,
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}
    return UUID(response.json()["id"])


@pytest.fixture
async def owner_user_id(auth_client: AsyncClient, owner_token: str) -> UUID:
    response = await auth_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code in {HTTP_200_OK}
    return UUID(response.json()["id"])
