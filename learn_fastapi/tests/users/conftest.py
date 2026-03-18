import pytest
from httpx import AsyncClient


@pytest.fixture
def user_data() -> dict[str, str]:
    """Return default user credentials for users endpoints tests.

    Returns:
        A dictionary with email and password keys.

    """
    return {
        "email": "test@example.com",
        "password": "secure_password123",
    }


@pytest.fixture
async def registered_user(
    client: AsyncClient, user_data: dict[str, str]
) -> dict[str, str]:
    """Register and return a user JSON payload.

    Args:
        client: The AsyncClient fixture for making HTTP requests.
        user_data: The user credentials for registration.

    Returns:
        A dictionary with user details.

    """
    register_response = await client.post("/auth/register", json=user_data)
    return register_response.json()


@pytest.fixture
async def access_token(
    client: AsyncClient,
    user_data: dict[str, str],
    registered_user: dict[str, str],
) -> str:
    """Authenticate the registered user and return an access token.

    Args:
        client: The AsyncClient fixture for making HTTP requests.
        user_data: The user credentials for login.
        registered_user: The registered user details (ensures the user exists).

    Returns:
        A JWT access token string.

    """
    login_response = await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )
    return login_response.json()["access_token"]


@pytest.fixture
def auth_headers(access_token: str) -> dict[str, str]:
    """Return Authorization header for authenticated requests.

    Args:
        access_token: The JWT access token string.

    Returns:
        A dictionary with the Authorization header.

    """
    return {"Authorization": f"Bearer {access_token}"}
