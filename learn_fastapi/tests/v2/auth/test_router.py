from http import HTTPStatus

from httpx import AsyncClient

# ---------------------------------------------------------------------------
# POST /auth/token/  (v2)
# ---------------------------------------------------------------------------


class TestLogin:
    async def test_login_success(self, client: AsyncClient) -> None:
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

        # Fields present in v1 Token
        assert data["access_token"] is not None
        assert data["access_token"]
        assert data["csrf_token"] is not None
        assert data["csrf_token"]

        # New fields in TokenV2
        assert data["access_token_type"] == "bearer"  # noqa: S105
        assert isinstance(data["access_expires_in"], int)
        assert data["access_expires_in"] > 0
        assert data["refresh_token"] is not None
        assert data["refresh_token"]
        assert isinstance(data["refresh_expires_in"], int)
        assert data["refresh_expires_in"] > 0

        # refresh_token cookie must still be set (used by /auth/refresh)
        assert client.cookies.get("refresh_token") is not None

    async def test_login_wrong_password(self, client: AsyncClient) -> None:
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

    async def test_login_nonexistent_user(self, client: AsyncClient) -> None:
        response = await client.post(
            "/auth/token",
            data={
                "username": "nonexistent@example.com",
                "password": "any_password",
            },
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]
