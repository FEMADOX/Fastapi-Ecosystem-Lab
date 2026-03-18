from http import HTTPStatus

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.auth.utils import verify_password
from learn_fastapi.src.users.models import User


class TestMe:
    async def test_get_me_authenticated(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        user_data: dict[str, str],
    ) -> None:
        response = await client.get(
            "/users/me",
            headers=auth_headers,
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["is_active"] is True

    async def test_get_me_unauthenticated(self, client: AsyncClient) -> None:
        response = await client.get("/users/me")

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_get_me_invalid_token(self, client: AsyncClient) -> None:
        response = await client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"},
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid or expired token" in response.json()["detail"]

    async def test_update_me(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        auth_headers: dict[str, str],
        registered_user: dict[str, str],
        user_data: dict[str, str],
    ) -> None:
        old_user_data = user_data.copy()
        response = await client.patch(
            f"/users/{registered_user['id']}",
            headers=auth_headers,
            json={
                "current_password": "secure_password123",
                "new_email": "newemailtest@example.com",
                "new_password": "new_secure_password123",
            },
        )
        assert response.status_code == HTTPStatus.OK

        new_user_data = response.json()
        assert new_user_data["email"] == "newemailtest@example.com"

        statement = select(User).where(User.email == "newemailtest@example.com")
        result = await test_session.execute(statement)
        updated_user = result.scalar_one()
        assert verify_password("new_secure_password123", updated_user.password_hash)
        assert not verify_password(
            old_user_data["password"], updated_user.password_hash
        )

    async def test_delete_me(
        self,
        client: AsyncClient,
        test_session: AsyncSession,
        auth_headers: dict[str, str],
        registered_user: dict[str, str],
        user_data: dict[str, str],
    ) -> None:
        response = await client.request(
            "DELETE",
            f"/users/{registered_user['id']}",
            headers=auth_headers,
            json={"password": user_data["password"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT

        statement = select(User).where(User.email == user_data["email"])
        result = await test_session.execute(statement)
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None
