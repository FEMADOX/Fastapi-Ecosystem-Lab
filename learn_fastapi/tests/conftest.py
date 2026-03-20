"""Global test configuration shared across all test modules."""

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from learn_fastapi.src.database import Base, get_session
from learn_fastapi.src.main import app

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator
    from types import TracebackType

    from httpx import Response
    from sqlalchemy.ext.asyncio import (
        AsyncEngine,
        AsyncSession,
    )

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_API_PREFIX = "/v1"


class PrefixedAsyncClient(AsyncClient):
    """AsyncClient that auto-prefixes API routes for tests.

    Tests can keep calling ``/auth/...`` or ``/items/...`` while the app
    routes are mounted under ``/v1``.
    """

    def __init__(
        self,
        transport: ASGITransport | None = None,
        base_url: str = "http://testserver",
        api_prefix: str = TEST_API_PREFIX,
    ) -> None:
        """Initialize the client with an optional route prefix for test calls."""
        if transport is None:
            transport = ASGITransport(app)

        super().__init__(transport=transport, base_url=base_url)
        self.api_prefix = api_prefix

    def _with_api_prefix(self, url: str) -> str:
        if url.startswith(("http://", "https://")):
            return url
        if url.startswith(self.api_prefix):
            return url
        if url.startswith("/"):
            return f"{self.api_prefix}{url}"
        return f"{self.api_prefix}/{url}"

    async def request(
        self, method: str, url: str, *args: object, **kwargs: object
    ) -> Response:  # type: ignore[override]
        return await super().request(
            method,
            self._with_api_prefix(str(url)),
            *args,
            **kwargs,  # ty: ignore[invalid-argument-type]
        )


class ClientContext:
    """Reusable async context manager for test clients with dependency overrides."""

    def __init__(
        self,
        *,
        api_prefix: str,
        test_session: AsyncSession,
        dependency_overrides: dict[Callable[..., object], Callable[..., object]]
        | None = None,
    ) -> None:
        """Initialize client settings and optional dependency overrides."""
        self._test_session = test_session
        self._api_prefix = api_prefix
        self._dependency_overrides = dependency_overrides or {}
        self._previous_overrides: dict[
            Callable[..., object], Callable[..., object]
        ] = {}
        self._client = PrefixedAsyncClient(api_prefix=api_prefix)

    def _override_get_async_session(self) -> Generator[AsyncSession]:
        yield self._test_session

    async def __aenter__(self) -> AsyncClient:
        """Apply overrides and enter the HTTP client context.

        Returns:
            A configured async test client with dependency overrides applied.

        """
        self._previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_session] = self._override_get_async_session
        app.dependency_overrides.update(self._dependency_overrides)
        return await self._client.__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Restore previous overrides and close the client context."""
        await self._client.__aexit__(exc_type, exc, tb)
        app.dependency_overrides = self._previous_overrides


@pytest.fixture
def client_context_factory(
    test_session: AsyncSession,
) -> Callable[..., ClientContext]:
    """Return a factory for creating test clients bound to the current session.

    Returns:
        A callable that creates ``TestClientContext`` instances sharing the
        current test session.

    """

    def build_context(
        *,
        api_prefix: str = TEST_API_PREFIX,
        dependency_overrides: dict[Callable[..., object], Callable[..., object]]
        | None = None,
    ) -> ClientContext:
        return ClientContext(
            test_session=test_session,
            api_prefix=api_prefix,
            dependency_overrides=dependency_overrides,
        )

    return build_context


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
        autocommit=False,
        autoflush=False,
        bind=test_async_engine,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(
    client_context_factory: Callable[..., ClientContext],
) -> AsyncGenerator[AsyncClient]:
    """Return a TestClient bound to the learn_fastapi app.

    This fixture is shared across all test modules.

    Args:
        client_context_factory: Factory that creates a test client context.

    Yields:
        Configured AsyncClient instance.

    """
    async with client_context_factory(api_prefix=TEST_API_PREFIX) as async_client:
        yield async_client
