from http import HTTPStatus

from httpx import AsyncClient


async def test_register_user(client: AsyncClient) -> None:
    """Test successful user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "secure_password123",
    }

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "id" in data


async def test_register_duplicate_email(client: AsyncClient) -> None:
    """Test that registering with an existing email returns an error."""
    user_data = {
        "email": "test@example.com",
        "password": "secure_password123",
    }

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == HTTPStatus.CREATED

    response = await client.post("/auth/register", json=user_data)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


async def test_login_success(client: AsyncClient) -> None:
    """Test that a valid user can log in and receive a JWT token."""
    user_data = {
        "email": "test@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    response = await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"  # noqa: S105
    assert data["user"]["email"] == user_data["email"]


async def test_login_wrong_password(client: AsyncClient) -> None:
    """Test that login fails when the wrong password is provided."""
    user_data = {
        "email": "test@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    response = await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": "wrong_password",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


async def test_login_nonexistent_user(client: AsyncClient) -> None:
    """Test that login fails for a user that does not exist."""
    response = await client.post(
        "/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "any_password",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["detail"]


async def test_get_me_authenticated(client: AsyncClient) -> None:
    """Test that an authenticated user can retrieve their own profile."""
    user_data = {
        "email": "test@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    login_response = await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    token = login_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["is_active"] is True


async def test_get_me_unauthenticated(client: AsyncClient) -> None:
    """Test that accessing /me without a token returns 401."""
    response = await client.get("/auth/me")

    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_get_me_invalid_token(client: AsyncClient) -> None:
    """Test that accessing /me with an invalid token returns 401."""
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]
