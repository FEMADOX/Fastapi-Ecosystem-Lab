from typing import TYPE_CHECKING

from starlette.status import HTTP_200_OK

if TYPE_CHECKING:
    from collections.abc import Callable

    from learn_fastapi.tests.conftest import ClientContext


class TestSwaggerDocs:
    async def test_docs_returns_swagger_ui(
        self,
        client_context_factory: Callable[..., ClientContext],
    ) -> None:
        async with client_context_factory(api_prefix="") as client:
            response = await client.get("/docs")

        assert response.status_code == HTTP_200_OK
        assert "SwaggerUIBundle" in response.text

    async def test_docs_uses_adaptive_grid_layout(
        self,
        client_context_factory: Callable[..., ClientContext],
    ) -> None:
        async with client_context_factory(api_prefix="") as client:
            response = await client.get("/docs")

        assert "display: grid;" in response.text
        assert (
            "grid-template-columns: repeat(auto-fit, minmax(min(400px, 100%), 1fr));"
            in response.text
        )
