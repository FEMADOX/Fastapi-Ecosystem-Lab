from typing import TYPE_CHECKING

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_CONTENT,
)

from learn_fastapi.src.first_steps.router import DB

if TYPE_CHECKING:
    from starlette.testclient import TestClient

# ---------------------------------------------------------------------------
# GET /items/hello-world/
# ---------------------------------------------------------------------------


class TestHelloWorld:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/items/hello-world/")
        assert response.status_code == HTTP_200_OK

    def test_response_body(self, client: TestClient) -> None:
        response = client.get("/items/hello-world/")
        assert response.json() == {"message": "Hello World"}


# ---------------------------------------------------------------------------
# GET /items/
# ---------------------------------------------------------------------------


class TestReadItems:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.get("/items/")
        assert response.status_code == HTTP_200_OK

    def test_returns_dict(self, client: TestClient) -> None:
        response = client.get("/items/")
        assert isinstance(response.json(), dict)

    def test_items_have_required_fields(self, client: TestClient) -> None:
        items = client.get("/items/").json()
        for item in items.values():
            assert "name" in item
            assert "price" in item

    def test_returns_all_seeded_items(self, client: TestClient) -> None:
        response = client.get("/items/")
        data = response.json()
        # The seeded database.json has at least the 5 initial entries
        db_max_len = 5
        assert len(data) >= db_max_len


# ---------------------------------------------------------------------------
# GET /items/{id_param}
# ---------------------------------------------------------------------------


class TestReadItem:
    def test_existing_integer_id(self, client: TestClient) -> None:
        """Keys '1', '2', '3' are present in the seeded JSON."""
        response = client.get("/items/1")
        assert response.status_code == HTTP_200_OK

    def test_existing_item_has_correct_name(self, client: TestClient) -> None:
        response = client.get("/items/1")
        assert response.json()["name"] == "Foo"

    def test_non_existing_id_returns_404(self, client: TestClient) -> None:
        """An ID that does not exist must return 404 Not Found."""
        response = client.get("/items/9999")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_invalid_id_type_returns_422(self, client: TestClient) -> None:
        """A non-integer, non-UUID value must fail validation."""
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
        names_in_db = {item.name for item in DB.values()}
        assert sample_item["name"] in names_in_db

    def test_missing_required_field_returns_422(self, client: TestClient) -> None:
        """Omitting 'price' (required) must trigger a validation error."""
        response = client.post("/items/", json={"name": "Incomplete"})
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT

    def test_optional_fields_default_to_none(self, client: TestClient) -> None:
        payload = {"name": "Minimal", "price": 5.0}
        response = client.post("/items/", json=payload)
        assert response.status_code in {HTTP_200_OK, HTTP_201_CREATED}
        body = response.json()
        assert body["tax"] == 0.00


# ---------------------------------------------------------------------------
# PUT /items/{id_param}
# ---------------------------------------------------------------------------


class TestUpdateItem:
    def test_returns_200(self, client: TestClient, sample_item: dict) -> None:
        response = client.put("/items/1", json=sample_item)
        assert response.status_code == HTTP_200_OK

    def test_response_reflects_update(
        self,
        client: TestClient,
        sample_item: dict,
    ) -> None:
        response = client.put("/items/1", json=sample_item)
        body = response.json()
        assert body["name"] == sample_item["name"]
        assert body["price"] == sample_item["price"]

    def test_update_persisted_in_db(
        self,
        client: TestClient,
        sample_item: dict,
    ) -> None:
        client.put("/items/1", json=sample_item)
        assert DB["1"].name == sample_item["name"]

    def test_invalid_payload_returns_422(self, client: TestClient) -> None:
        response = client.put("/items/1", json={"name": "Bad", "price": "not-a-float"})
        assert response.status_code == HTTP_422_UNPROCESSABLE_CONTENT


# ---------------------------------------------------------------------------
# DELETE /items/{id_param}
# ---------------------------------------------------------------------------


class TestDeleteItem:
    def test_returns_200(self, client: TestClient) -> None:
        response = client.delete("/items/1")
        assert response.status_code == HTTP_200_OK

    def test_response_is_deleted_item(self, client: TestClient) -> None:
        response = client.delete("/items/1")
        body = response.json()
        assert body["name"] == "Foo"

    def test_item_removed_from_db(self, client: TestClient) -> None:
        client.delete("/items/1")
        assert "1" not in DB

    def test_delete_non_existing_id_returns_404(self, client: TestClient) -> None:
        response = client.delete("/items/9999")
        assert response.status_code == HTTP_404_NOT_FOUND
