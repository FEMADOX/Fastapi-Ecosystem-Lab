import uuid
from typing import TYPE_CHECKING

import pytest
from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from learn_fastapi.src.constants import IMAGES_DIR

if TYPE_CHECKING:
    from collections.abc import Generator

    from starlette.testclient import TestClient

    from learn_fastapi.src.first_steps.models import Item as ItemModel


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------


class TestHelloWorld:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK

    def test_response_body(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.json() == {"message": "Hello World"}


# ---------------------------------------------------------------------------
# GET /items/
# ---------------------------------------------------------------------------


class TestReadItems:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/items/")
        assert response.status_code == HTTP_200_OK

    def test_returns_list(self, client: TestClient) -> None:
        response = client.get("/items/")
        assert isinstance(response.json(), list)

    def test_items_have_required_fields(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        items = client.get("/items/").json()
        for item in items:
            assert "name" in item
            assert "price" in item

    def test_returns_seeded_item(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.get("/items/")
        names = [item["name"] for item in response.json()]
        assert "Foo" in names


# ---------------------------------------------------------------------------
# GET /items/{id_param}
# ---------------------------------------------------------------------------


class TestReadItem:
    def test_existing_item(self, client: TestClient, seeded_item: ItemModel) -> None:
        response = client.get(f"/items/{seeded_item.id}")
        assert response.status_code == HTTP_200_OK

    def test_existing_item_has_correct_name(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.get(f"/items/{seeded_item.id}")
        assert response.json()["name"] == "Foo"

    def test_non_existing_id_returns_404(self, client: TestClient) -> None:
        """A valid UUID that does not exist in the DB must return 404."""
        random_id = uuid.uuid4()
        response = client.get(f"/items/{random_id}")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_invalid_id_type_returns_422(self, client: TestClient) -> None:
        """A non-UUID value must fail validation."""
        response = client.get("/items/not-an-id")
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# ---------------------------------------------------------------------------
# POST /items/
# ---------------------------------------------------------------------------


class TestCreateItem:
    def test_returns_201_or_200(self, client: TestClient, sample_item: dict) -> None:
        response = client.post("/items/", json=sample_item)
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}

    def test_response_matches_payload(
        self,
        client: TestClient,
        sample_item: dict,
    ) -> None:
        response = client.post("/items/", json=sample_item)
        body = response.json()
        assert body["name"] == sample_item["name"]
        assert body["price"] == sample_item["price"]
        assert body["tax"] == sample_item["tax"]

    def test_item_persisted_in_db(self, client: TestClient, sample_item: dict) -> None:
        client.post("/items/", json=sample_item)
        names = [item["name"] for item in client.get("/items/").json()]
        assert sample_item["name"] in names

    def test_missing_required_field_returns_422(self, client: TestClient) -> None:
        """Omitting 'price' (required) must trigger a validation error."""
        response = client.post("/items/", json={"name": "Incomplete"})
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT

    def test_optional_fields_use_defaults(self, client: TestClient) -> None:
        payload = {"name": "Minimal", "price": 5.0}
        response = client.post("/items/", json=payload)
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}
        body = response.json()
        body_tax = 0.00
        assert body["tax"] == body_tax


# ---------------------------------------------------------------------------
# PUT /items/{id_param}
# ---------------------------------------------------------------------------


class TestUpdateItem:
    def test_returns_200(
        self, client: TestClient, sample_item: dict, seeded_item: ItemModel
    ) -> None:
        response = client.put(f"/items/{seeded_item.id}", json=sample_item)
        assert response.status_code == HTTP_200_OK

    def test_response_reflects_update(
        self,
        client: TestClient,
        sample_item: dict,
        seeded_item: ItemModel,
    ) -> None:
        response = client.put(f"/items/{seeded_item.id}", json=sample_item)
        body = response.json()
        assert body["name"] == sample_item["name"]
        assert body["price"] == sample_item["price"]

    def test_update_persisted_in_db(
        self,
        client: TestClient,
        sample_item: dict,
        seeded_item: ItemModel,
    ) -> None:
        client.put(f"/items/{seeded_item.id}", json=sample_item)
        body = client.get(f"/items/{seeded_item.id}").json()
        assert body["name"] == sample_item["name"]

    def test_invalid_payload_returns_422(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.put(
            f"/items/{seeded_item.id}", json={"name": "Bad", "price": "not-a-float"}
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# ---------------------------------------------------------------------------
# DELETE /items/{id_param}
# ---------------------------------------------------------------------------


class TestDeleteItem:
    def test_returns_200(self, client: TestClient, seeded_item: ItemModel) -> None:
        response = client.delete(f"/items/{seeded_item.id}")
        assert response.status_code == HTTP_200_OK

    def test_response_contains_detail(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.delete(f"/items/{seeded_item.id}")
        body = response.json()
        assert body["detail"] == "Item deleted successfully"
        assert body["status_code"] == HTTP_200_OK

    def test_item_removed_from_db(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        client.delete(f"/items/{seeded_item.id}")
        response = client.get(f"/items/{seeded_item.id}")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_delete_non_existing_id_returns_404(self, client: TestClient) -> None:
        random_id = uuid.uuid4()
        response = client.delete(f"/items/{random_id}")
        assert response.status_code == HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# POST /items/image/{id_param}
# ---------------------------------------------------------------------------


class TestSubmitItemImage:
    FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    @pytest.fixture(autouse=True)
    def cleanup_images(self) -> Generator[None]:
        before = set(IMAGES_DIR.iterdir()) if IMAGES_DIR.exists() else set()
        yield
        if IMAGES_DIR.exists():
            for f in IMAGES_DIR.iterdir():
                if f not in before:
                    f.unlink(missing_ok=True)

    def test_returns_200(self, client: TestClient, seeded_item: ItemModel) -> None:
        response = client.post(
            f"/items/image/{seeded_item.id}",
            files={"image_file": ("test.png", self.FAKE_PNG, "image/png")},
        )
        assert response.status_code == HTTP_200_OK

    def test_image_url_set(self, client: TestClient, seeded_item: ItemModel) -> None:
        response = client.post(
            f"/items/image/{seeded_item.id}",
            files={"image_file": ("test.png", self.FAKE_PNG, "image/png")},
        )
        assert response.json()["image_url"] == "/static/images/test.png"

    def test_item_name_unchanged(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.post(
            f"/items/image/{seeded_item.id}",
            files={"image_file": ("test.png", self.FAKE_PNG, "image/png")},
        )
        assert response.json()["name"] == "Foo"

    def test_non_existing_id_returns_404(self, client: TestClient) -> None:
        random_id = uuid.uuid4()
        response = client.post(
            f"/items/image/{random_id}",
            files={"image_file": ("test.png", self.FAKE_PNG, "image/png")},
        )
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_missing_file_returns_422(
        self, client: TestClient, seeded_item: ItemModel
    ) -> None:
        response = client.post(f"/items/image/{seeded_item.id}")
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# ---------------------------------------------------------------------------
# POST /items/with-image/
# ---------------------------------------------------------------------------


class TestCreateItemWithImage:
    FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

    @pytest.fixture(autouse=True)
    def cleanup_images(self) -> Generator[None]:
        before = set(IMAGES_DIR.iterdir()) if IMAGES_DIR.exists() else set()
        yield
        if IMAGES_DIR.exists():
            for f in IMAGES_DIR.iterdir():
                if f not in before:
                    f.unlink(missing_ok=True)

    def test_returns_200_without_image(self, client: TestClient) -> None:
        response = client.post(
            "/items/with-image/",
            data={
                "name": "Test Item",
                "description": "A long enough description",
                "price": "9.99",
                "tax": "1.0",
            },
        )
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}

    def test_response_fields_without_image(self, client: TestClient) -> None:
        response = client.post(
            "/items/with-image/",
            data={
                "name": "Test Item",
                "description": "A long enough description",
                "price": "9.99",
                "tax": "1.0",
            },
        )
        body = response.json()
        body_price = 9.99
        assert body["name"] == "Test Item"
        assert body["price"] == body_price
        assert body["image_url"] == ""

    def test_returns_200_with_image(self, client: TestClient) -> None:
        response = client.post(
            "/items/with-image/",
            data={
                "name": "Image Item",
                "description": "A long enough description",
                "price": "5.00",
            },
            files={"image_file": ("product.png", self.FAKE_PNG, "image/png")},
        )
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}

    def test_image_url_set_when_file_provided(self, client: TestClient) -> None:
        response = client.post(
            "/items/with-image/",
            data={
                "name": "Image Item",
                "description": "A long enough description",
                "price": "5.00",
            },
            files={"image_file": ("product.png", self.FAKE_PNG, "image/png")},
        )
        assert response.json()["image_url"] == "/static/images/product.png"

    def test_default_values_used_when_no_data_sent(self, client: TestClient) -> None:
        response = client.post("/items/with-image/")
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}
        body = response.json()
        body_price = 0.00
        assert body["name"] == "Default Item"
        assert body["price"] == body_price
        assert body["image_url"] == ""

    def test_item_persisted_in_db(self, client: TestClient) -> None:
        client.post(
            "/items/with-image/",
            data={
                "name": "Persisted Item",
                "description": "A long enough description",
                "price": "3.00",
            },
        )
        names = [item["name"] for item in client.get("/items/").json()]
        assert "Persisted Item" in names

    def test_negative_price_returns_422(self, client: TestClient) -> None:
        """Price has a ge=0 constraint — a negative value must fail validation."""
        response = client.post(
            "/items/with-image/",
            data={
                "name": "Bad Price",
                "description": "A long enough description",
                "price": "-1.00",
            },
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT
