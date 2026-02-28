from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.requests import Request

# Inyecta el script de arel en el HTML del Swagger
JS_CODE = (Path(__file__).parent / "static" / "js" / "reloadScript.js").read_text()
RELOAD_SCRIPT = "<script>" + JS_CODE + "</script>"


class SwaggerHotReloadMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> HTMLResponse | Response:
        response = await call_next(request)
        if request.url.path == "/docs" and "text/html" in response.headers.get(
            "content-type",
            "",
        ):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            body = body.replace(b"</body>", f"{RELOAD_SCRIPT}</body>".encode())
            return HTMLResponse(content=body.decode())
        return response
