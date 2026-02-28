import asyncio
import tempfile
from typing import TYPE_CHECKING

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from learn_fastapi.src.database import Base, get_async_session
from learn_fastapi.src.first_steps.models import Item as ItemModel
from learn_fastapi.src.first_steps.my_app import app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


# ---------------------------------------------------------------------------
# Test database setup
# ---------------------------------------------------------------------------

_tmp_dir = tempfile.mkdtemp()
_TEST_DB_URL = f"sqlite+aiosqlite:///{_tmp_dir}/test_database.db"
_test_engine = create_async_engine(
    _TEST_DB_URL, connect_args={"check_same_thread": False}
)
_TestAsyncSessionMaker = async_sessionmaker(
    autocommit=False, autoflush=False, bind=_test_engine
)


async def _override_get_async_session() -> AsyncGenerator[AsyncSession]:
    async with _TestAsyncSessionMaker() as session:
        yield session


app.dependency_overrides[get_async_session] = _override_get_async_session


async def _create_tables() -> None:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def _drop_tables() -> None:
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _seed_item() -> ItemModel:
    async with _TestAsyncSessionMaker() as session:
        item = ItemModel(
            name="Foo",
            description="Seeded test item description",
            price=10.0,
            tax=1.0,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return item


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def setup_test_db() -> Generator:
    """Create all tables before each test and drop them afterwards.

    This guarantees a completely clean database state for every test,
    preventing pollution between tests.

    Yields:
        Generator: Yields control to the test, then tears down the schema.

    """
    asyncio.run(_create_tables())
    yield
    asyncio.run(_drop_tables())


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient bound to the first_steps learn_fastapi app.

    Returns:
        TestClient: A TestClient instance for the app.

    """
    return TestClient(app)


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
def seeded_item(setup_test_db: None) -> ItemModel:
    """Insert a single 'Foo' item into the test DB and return the ORM instance.

    Depends on setup_test_db to ensure tables exist before seeding.

    Args:
        setup_test_db: The autouse fixture that creates the schema.

    Returns:
        ItemModel: The persisted ORM instance (with its generated UUID).

    """
    return asyncio.run(_seed_item())
