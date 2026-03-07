from httpx import AsyncClient
from starlette.status import HTTP_200_OK

# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------


class TestHelloWorld:
    async def test_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/")
        assert response.status_code == HTTP_200_OK

    async def test_response_body(self, client: AsyncClient) -> None:
        response = await client.get("/")
        assert response.json() == {"message": "Hello World"}
