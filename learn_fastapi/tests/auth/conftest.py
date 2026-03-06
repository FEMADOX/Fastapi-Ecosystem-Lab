import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from learn_fastapi.src.auth.models import User
from learn_fastapi.src.auth.utils import hash_password


@pytest.fixture
async def seeded_user(test_session: AsyncSession, client: AsyncClient) -> User:
    """Create a test user in the database.

    Args:
        test_session: The test database session (from global fixture).
        client: The test HTTP client (dependency to ensure DB setup).

    Returns:
        User: The persisted user instance.

    """
    user = User(
        email="repeatedemail@gmail.com",
        password_hash=hash_password("mysupersecurepass"),
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user
