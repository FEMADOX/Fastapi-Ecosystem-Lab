from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.auth.models import RefreshToken
from learn_fastapi.src.auth.utils import verify_refresh_token

# ---------------------------------------------------------------------------
# POST /auth/register/
# ---------------------------------------------------------------------------


class TestRegister:
    async def test_register_user(self, client: AsyncClient) -> None:
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

    async def test_register_duplicate_email(self, client: AsyncClient) -> None:
        user_data = {
            "email": "test@example.com",
            "password": "secure_password123",
        }

        response = await client.post("/auth/register", json=user_data)
        assert response.status_code == HTTPStatus.CREATED

        response = await client.post("/auth/register", json=user_data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]


# ---------------------------------------------------------------------------
# POST /auth/token/
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
        assert "access_token" in data
        assert data["token_type"] == "bearer"  # noqa: S105
        assert data["access_token"] is not None

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


# ---------------------------------------------------------------------------
# POST /auth/refresh/
# ---------------------------------------------------------------------------


class TestRefresh:
    async def test_refresh_success_rotates_tokens(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
    ) -> None:
        user_data = {
            "email": "refresh_success@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)

        login_response = await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        assert login_response.status_code == HTTPStatus.OK

        initial_csrf = login_response.json()["csrf_token"]
        initial_refresh = client.cookies.get("refresh_token")
        assert initial_refresh is not None

        refresh_response = await client.post(
            "/auth/refresh",
            headers={"X-CSRF-Token": initial_csrf},
        )

        assert refresh_response.status_code == HTTPStatus.OK
        body = refresh_response.json()
        assert body["token_type"] == "bearer"  # noqa: S105
        assert body["access_token"]
        assert body["csrf_token"]

        rotated_refresh = client.cookies.get("refresh_token")
        rotated_csrf = client.cookies.get("csrf_token")
        assert rotated_refresh is not None
        assert rotated_csrf is not None
        assert rotated_refresh != initial_refresh
        assert rotated_csrf == body["csrf_token"]

        result = await test_session.execute(select(RefreshToken))  # ty:ignore[invalid-argument-type]
        tokens = result.scalars().all()
        total_tokens = 2
        assert len(tokens) == total_tokens

        old_token = next(
            token
            for token in tokens
            if verify_refresh_token(initial_refresh, token.token_hash)
        )
        assert old_token.revoked_at is not None
        assert any(token.revoked_at is None for token in tokens)

    async def test_refresh_missing_csrf_header_returns_422(
        self,
        client: AsyncClient,
    ) -> None:
        user_data = {
            "email": "refresh_missing_header@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        response = await client.post("/auth/refresh")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    async def test_refresh_with_mismatched_csrf_token_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        user_data = {
            "email": "refresh_mismatch_csrf@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        response = await client.post(
            "/auth/refresh",
            headers={"X-CSRF-Token": "invalid-csrf"},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid refresh token or CSRF token" in response.json()["detail"]

    async def test_refresh_missing_refresh_cookie_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        user_data = {
            "email": "refresh_missing_cookie@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        login_response = await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        csrf = login_response.json()["csrf_token"]

        client.cookies.pop("refresh_token", None)

        response = await client.post("/auth/refresh", headers={"X-CSRF-Token": csrf})

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid refresh token or CSRF token" in response.json()["detail"]

    async def test_refresh_with_invalid_refresh_cookie_returns_401(
        self,
        client: AsyncClient,
    ) -> None:
        user_data = {
            "email": "refresh_invalid_cookie@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        login_response = await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        csrf = login_response.json()["csrf_token"]
        client.cookies["refresh_token"] = "invalid-refresh-token"

        response = await client.post("/auth/refresh", headers={"X-CSRF-Token": csrf})

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid or expired refresh token" in response.json()["detail"]


# ---------------------------------------------------------------------------
# POST /auth/logout/
# ---------------------------------------------------------------------------


class TestLogout:
    async def test_logout_success_revokes_token_and_clears_cookies(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
    ) -> None:
        user_data = {
            "email": "logout_success@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)

        login_response = await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )
        assert login_response.status_code == HTTPStatus.OK

        csrf_token = login_response.json()["csrf_token"]

        logout_response = await client.post(
            "/auth/logout",
            headers={"X-CSRF-Token": csrf_token},
        )

        assert logout_response.status_code == HTTPStatus.NO_CONTENT

        result = await test_session.execute(select(RefreshToken))  # ty:ignore[invalid-argument-type]
        tokens = result.scalars().all()
        assert len(tokens) == 1
        assert tokens[0].revoked_at is not None

        set_cookie_headers = logout_response.headers.get_list("set-cookie")
        assert any("refresh_token=" in header for header in set_cookie_headers)
        assert any("csrf_token=" in header for header in set_cookie_headers)

    async def test_logout_without_csrf_token_does_not_revoke(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
    ) -> None:
        user_data = {
            "email": "logout_missing_csrf@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        logout_response = await client.post("/auth/logout")

        assert logout_response.status_code == HTTPStatus.NO_CONTENT

        result = await test_session.execute(select(RefreshToken))  # ty:ignore[invalid-argument-type]
        tokens = result.scalars().all()
        assert len(tokens) == 1
        assert tokens[0].revoked_at is None

    async def test_logout_with_invalid_csrf_token_does_not_revoke(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
    ) -> None:
        user_data = {
            "email": "logout_invalid_csrf@example.com",
            "password": "secure_password123",
        }
        await client.post("/auth/register", json=user_data)
        await client.post(
            "/auth/token",
            data={"username": user_data["email"], "password": user_data["password"]},
        )

        logout_response = await client.post(
            "/auth/logout",
            headers={"X-CSRF-Token": "wrong_token"},
        )

        assert logout_response.status_code == HTTPStatus.NO_CONTENT

        result = await test_session.execute(select(RefreshToken))  # ty:ignore[invalid-argument-type]
        tokens = result.scalars().all()
        assert len(tokens) == 1
        assert tokens[0].revoked_at is None

    async def test_logout_without_cookies_returns_204_and_clear_headers(
        self,
        client: AsyncClient,
    ) -> None:
        logout_response = await client.post("/auth/logout")

        assert logout_response.status_code == HTTPStatus.NO_CONTENT

        set_cookie_headers = logout_response.headers.get_list("set-cookie")
        assert any("refresh_token=" in header for header in set_cookie_headers)
        assert any("csrf_token=" in header for header in set_cookie_headers)


# ---------------------------------------------------------------------------
# GET /auth/me/
# ---------------------------------------------------------------------------


class TestMe:
    async def test_get_me_authenticated(self, client: AsyncClient) -> None:
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

    async def test_get_me_unauthenticated(self, client: AsyncClient) -> None:
        response = await client.get("/auth/me")

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_me_invalid_token(self, client: AsyncClient) -> None:
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid or expired token" in response.json()["detail"]
