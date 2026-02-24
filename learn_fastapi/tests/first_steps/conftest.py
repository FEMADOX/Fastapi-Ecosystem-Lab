from typing import TYPE_CHECKING

import pytest
from starlette.testclient import TestClient

from learn_fastapi.src.database import DB_PATH
from learn_fastapi.src.first_steps.my_app import app
from learn_fastapi.src.first_steps.router import DB
from learn_fastapi.src.first_steps.schema import Item

if TYPE_CHECKING:
    from collections.abc import Generator


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


@pytest.fixture(autouse=True)
def restore_db() -> Generator:
    """Restore the in-memory DB *and* database.json after each test.

    This prevents write operations (POST, PUT, DELETE) from polluting
    subsequent tests or the actual data file.

    Yields:
        Generator: A generator that yields control to the test and then
            restores the in-memory DB and database.json.

    """
    # Snapshot the in-memory dict
    snapshot: dict[str, Item] = dict(DB)
    # Snapshot the JSON file on disk
    disk_snapshot: str = DB_PATH.read_text(encoding="utf-8")
    yield
    # Restore in-memory state
    DB.clear()
    DB.update(snapshot)
    # Restore disk state
    DB_PATH.write_text(disk_snapshot, encoding="utf-8")
