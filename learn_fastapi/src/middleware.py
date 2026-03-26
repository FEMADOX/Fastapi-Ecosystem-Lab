from typing import TYPE_CHECKING, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .constants import JS_DIR

if TYPE_CHECKING:
    from collections.abc import Callable

    from starlette.middleware import _MiddlewareFactory
    from starlette.requests import Request

# Inyecta el script de arel en el HTML del Swagger
JS_CODE = (JS_DIR / "reloadScript.js").read_text()
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


class CorsMiddlewareConfigurer:
    def __init__(self, allowed_hosts: list[str]) -> None:
        """Initialize default CORS settings for local development and configured hosts.

        - `allow_origins`: Starts with localhost for frontend development and
            extends with hosts from settings.
        - `allow_methods`: Allows all HTTP methods.
        - `allow_headers`: Allows all headers.
        - `allow_credentials`: Enables credentials support for cookies and
            authentication.
        This setup ensures a secure and flexible CORS configuration suitable
            for both development and production environments.

        Args:
            allowed_hosts: List of allowed hosts

        """
        self.allow_origins: list[str] = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
        self.allow_origins.extend(allowed_hosts)
        self.allow_methods = ["*"]
        self.allow_headers = ["*"]
        self.allow_credentials = True

    def add_middleware(self, app: FastAPI) -> None:
        app.add_middleware(
            cast("_MiddlewareFactory", CORSMiddleware),
            allow_origins=self.allow_origins,
            allow_methods=self.allow_methods,
            allow_headers=self.allow_headers,
            allow_credentials=self.allow_credentials,
        )
