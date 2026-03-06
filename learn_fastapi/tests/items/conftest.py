import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.items.models import Item as ItemModel


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
async def seeded_item(test_session: AsyncSession) -> ItemModel:
    """Insert a single 'Foo' item into the test DB.

    Args:
        test_session: The test database session (from global fixture).

    Returns:
        ItemModel: The persisted ORM instance with its UUID.

    """
    item = ItemModel(
        name="Foo",
        description="Seeded test item description",
        price=10.0,
        tax=1.0,
    )
    test_session.add(item)
    await test_session.commit()
    await test_session.refresh(item)
    return item
