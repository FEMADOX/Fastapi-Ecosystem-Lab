from typing import TYPE_CHECKING

import pytest

from learn_fastapi.src.shared.infrastructure.argon2_password_hasher import (
    Argon2PasswordHasher,
)
from learn_fastapi.src.users.models import User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession


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
        password_hash=Argon2PasswordHasher().hash("mysupersecurepass"),
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user
