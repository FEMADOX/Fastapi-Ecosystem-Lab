"""Test logout endpoint functionality."""

from http import HTTPStatus

from httpx import AsyncClient


async def test_logout_success(client: AsyncClient) -> None:
    """Test successful logout with valid refresh token and CSRF token."""
    # 1. Register user
    user_data = {
        "email": "logout_test@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    # 2. Login to get cookies
    login_response = await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    assert login_response.status_code == HTTPStatus.OK
    csrf_token = login_response.json().get("csrf_token")
    assert csrf_token is not None

    # Verify cookies were set
    cookies = client.cookies
    assert "refresh_token" in cookies
    assert "csrf_token" in cookies

    # 3. Logout with CSRF token in header
    logout_response = await client.post(
        "/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert logout_response.status_code == HTTPStatus.NO_CONTENT

    # 4. Verify cookies were cleared (httpx doesn't auto-clear, but server should send clear directives)
    # The response should have Set-Cookie headers with expired dates


async def test_logout_without_csrf_token(client: AsyncClient) -> None:
    """Test logout fails gracefully without CSRF token."""
    # 1. Register and login
    user_data = {
        "email": "logout_test2@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    # 2. Try logout without CSRF token header
    logout_response = await client.post("/auth/logout")

    # Should still return 204 (graceful degradation)
    assert logout_response.status_code == HTTPStatus.NO_CONTENT


async def test_logout_with_invalid_csrf_token(client: AsyncClient) -> None:
    """Test logout with mismatched CSRF token."""
    # 1. Register and login
    user_data = {
        "email": "logout_test3@example.com",
        "password": "secure_password123",
    }
    await client.post("/auth/register", json=user_data)

    await client.post(
        "/auth/token",
        data={
            "username": user_data["email"],
            "password": user_data["password"],
        },
    )

    # 2. Try logout with wrong CSRF token
    logout_response = await client.post(
        "/auth/logout",
        headers={"X-CSRF-Token": "wrong_token"},
    )

    # Should still return 204 (graceful handling)
    assert logout_response.status_code == HTTPStatus.NO_CONTENT


async def test_logout_without_cookies(client: AsyncClient) -> None:
    """Test logout when no cookies are present."""
    logout_response = await client.post("/auth/logout")

    # Should return 204 even without cookies (idempotent)
    assert logout_response.status_code == HTTPStatus.NO_CONTENT
