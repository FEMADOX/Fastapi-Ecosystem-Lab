from uuid import UUID

from httpx import AsyncClient
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)


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
    assert register_response.status_code == HTTP_201_CREATED

    login_response = await client.post(
        "/auth/token",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == HTTP_200_OK

    token = login_response.json()["access_token"]
    assert token
    return token


class TestItemsAuthorization:
    async def test_put_requires_authenticated_user(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await auth_client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Updated",
                "description": "Updated desc",
                "price": 20.0,
                "tax": 2.0,
            },
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED

    async def test_patch_requires_authenticated_user(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await auth_client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Patched"},
        )
        assert response.status_code == HTTP_401_UNAUTHORIZED

    async def test_delete_requires_authenticated_user(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
    ) -> None:
        response = await auth_client.delete(f"/items/{owner_item_id}")
        assert response.status_code == HTTP_401_UNAUTHORIZED

    async def test_put_allows_only_owner(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        owner_response = await auth_client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Owner Updated",
                "description": "Owner update",
                "price": 25.0,
                "tax": 2.5,
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTP_200_OK

        non_owner_response = await auth_client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Other Updated",
                "description": "Should fail",
                "price": 30.0,
                "tax": 3.0,
            },
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTP_404_NOT_FOUND

    async def test_patch_allows_only_owner(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        owner_response = await auth_client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Owner Patched"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTP_200_OK

        non_owner_response = await auth_client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Other Patched"},
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTP_404_NOT_FOUND

    async def test_delete_allows_only_owner(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        owner_token: str,
        other_user_token: str,
    ) -> None:
        non_owner_response = await auth_client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {other_user_token}"},
        )
        assert non_owner_response.status_code == HTTP_404_NOT_FOUND

        owner_response = await auth_client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert owner_response.status_code == HTTP_200_OK
        assert owner_response.json()["detail"] == "Item deleted successfully"

    async def test_put_allows_admin_for_non_owned_item(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await auth_client.put(
            f"/items/{owner_item_id}",
            json={
                "name": "Admin Updated",
                "description": "Updated by admin",
                "price": 50.0,
                "tax": 5.0,
                "user_id": str(owner_item_id),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["name"] == "Admin Updated"

    async def test_patch_allows_admin_for_non_owned_item(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await auth_client.patch(
            f"/items/{owner_item_id}",
            json={"name": "Admin Patched", "description": "Patched by admin"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["description"] == "Patched by admin"

    async def test_delete_allows_admin_for_non_owned_item(
        self,
        auth_client: AsyncClient,
        owner_item_id: UUID,
        admin_token: str,
    ) -> None:
        response = await auth_client.delete(
            f"/items/{owner_item_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["detail"] == "Item deleted successfully"
