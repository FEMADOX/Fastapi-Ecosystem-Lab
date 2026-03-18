from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.auth.utils import verify_password
from learn_fastapi.src.users.models import User


class TestMe:
    @pytest.fixture(autouse=True)
    async def setup(self, client: AsyncClient) -> None:
        user_data = {
            "email": "test@example.com",
            "password": "secure_password123",
        }
        self.user_data = user_data

        register_response = await client.post("/auth/register", json=user_data)

        self.user: dict[str, str] = register_response.json()

        login_response = await client.post(
            "/auth/token",
            data={
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )

        self.access_token: str = login_response.json()["access_token"]

    async def test_get_me_authenticated(self, client: AsyncClient) -> None:
        response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {self.access_token}"},
        )

        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert data["email"] == self.user_data["email"]
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
        self, client: AsyncClient, test_session: AsyncSession
    ) -> None:
        old_user_data = self.user_data.copy()
        response = await client.patch(
            f"/users/{self.user['id']}",
            headers={"Authorization": f"Bearer {self.access_token}"},
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
        self, client: AsyncClient, test_session: AsyncSession
    ) -> None:
        response = await client.request(
            "DELETE",
            f"/users/{self.user['id']}",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"password": self.user_data["password"]},
        )
        assert response.status_code == HTTPStatus.NO_CONTENT

        statement = select(User).where(User.email == self.user_data["email"])
        result = await test_session.execute(statement)
        deleted_user = result.scalar_one_or_none()
        assert deleted_user is None
