from http import HTTPStatus
from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.users.models import User


async def register_and_login(client: AsyncClient, email: str, password: str) -> str:
    """Register a user and return a bearer access token.

    Args:
        client: Async test client.
        email: User email to register/login.
        password: User password to register/login.

    Returns:
        Access token for Authorization header.

    """
    register_response = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == HTTPStatus.CREATED

    login_response = await client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == HTTPStatus.OK

    token = login_response.json()["access_token"]
    assert token
    return token


@pytest.fixture
async def owner_token(client: AsyncClient) -> str:
    return await register_and_login(
        client,
        email="owner@example.com",
        password="owner_password_123",  # noqa: S106
    )


@pytest.fixture
async def other_user_token(client: AsyncClient) -> str:
    return await register_and_login(
        client,
        email="other@example.com",
        password="other_password_123",  # noqa: S106
    )


@pytest.fixture
async def admin_token(client: AsyncClient, test_session: AsyncSession) -> str:
    email = "admin@example.com"
    token = await register_and_login(
        client,
        email=email,
        password="admin_password_123",  # noqa: S106
    )

    result = await test_session.execute(select(User).where(User.email == email))
    admin_user = result.scalar_one()
    admin_user.is_superuser = True
    await test_session.commit()

    return token


@pytest.fixture
async def owner_item_id(client: AsyncClient, owner_token: str) -> UUID:
    response = await client.post(
        "/items/",
        json={
            "name": "Owner Item",
            "description": "Owned by owner",
            "price": 10.0,
            "tax": 1.0,
        },
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert response.status_code in {HTTPStatus.OK, HTTPStatus.CREATED}
    return UUID(response.json()["id"])


class TestItemsAuthorization:
    async def test_put_requires_authenticated_user(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Updated",
                "description": "Updated desc",
                "price": 20.0,
                "tax": 2.0,
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_patch_requires_authenticated_user(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Patched"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_delete_requires_authenticated_user(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await client.delete(f"/items/{owner_item_id}")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    async def test_put_allows_only_owner(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        owner_response = await client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Owner Updated",
                "description": "Owner update",
                "price": 25.0,
                "tax": 2.5,
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTPStatus.OK

        non_owner_response = await client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Other Updated",
                "description": "Should fail",
                "price": 30.0,
                "tax": 3.0,
            },
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTPStatus.NOT_FOUND

    async def test_patch_allows_only_owner(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        owner_response = await client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Owner Patched"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTPStatus.OK

        non_owner_response = await client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Other Patched"},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTPStatus.NOT_FOUND

    async def test_delete_allows_only_owner(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        non_owner_response = await client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTPStatus.NOT_FOUND

        owner_response = await client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTPStatus.OK
        assert owner_response.json()["detail"] == "Item deleted successfully"

    async def test_put_allows_admin_for_non_owned_item(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Admin Updated",
                "description": "Updated by admin",
                "price": 50.0,
                "tax": 5.0,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["name"] == "Admin Updated"

    async def test_patch_allows_admin_for_non_owned_item(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Admin Patched", "description": "Patched by admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["description"] == "Patched by admin"

    async def test_delete_allows_admin_for_non_owned_item(
        self,
        client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()["detail"] == "Item deleted successfully"
