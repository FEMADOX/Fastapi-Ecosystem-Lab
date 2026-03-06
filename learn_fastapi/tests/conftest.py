"""Global test configuration shared across all test modules."""

from collections.abc import AsyncGenerator, Generator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from learn_fastapi.src.database import Base, get_session
from learn_fastapi.src.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_async_engine() -> AsyncGenerator[AsyncEngine]:
    """Create a test async engine backed by SQLite in-memory.

    This fixture is shared across all test modules.
    Creates all tables before tests and drops them after.

    Yields:
        Configured AsyncEngine instance.

    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_async_engine: AsyncEngine) -> AsyncGenerator[AsyncSession]:
    """Create a test async session bound to the test engine.

    This fixture is shared across all test modules.

    Args:
        test_async_engine: The test database engine.

    Yields:
        Configured AsyncSession instance.

    """
    session_factory = async_sessionmaker(
        autocommit=False, autoflush=False, bind=test_async_engine
    )

    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Return a TestClient bound to the learn_fastapi app.

    This fixture is shared across all test modules.

    Yields:
        Configured AsyncClient instance.

    """

    def override_get_async_session() -> Generator[AsyncSession]:
        yield test_session

    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = override_get_async_session

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://testserver"
    ) as async_client:
        yield async_client

    app.dependency_overrides = previous_overrides
