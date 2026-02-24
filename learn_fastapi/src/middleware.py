import asyncio
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.websockets import WebSocket, WebSocketDisconnect
from watchfiles import DefaultFilter, PythonFilter

# Inyecta el script de arel en el HTML del Swagger
JS_CODE = (Path(__file__).parent / "assets" / "js" / "reloadScript.js").read_text()
RELOAD_SCRIPT = "<script>" + JS_CODE + "</script>"


class SwaggerHotReloadMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> HTMLResponse | Response:
        response = await call_next(request)
        if request.url.path == "/docs" and "text/html" in response.headers.get(
            "content-type", ""
        ):
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            body = body.replace(b"</body>", f"{RELOAD_SCRIPT}</body>".encode())
            return HTMLResponse(content=body.decode())
        return response


_clients: list[WebSocket] = []


async def _watch_files(match_path: str = ".") -> None:
    from watchfiles import awatch

    # class PythonFilter(DefaultFilter):
    #     allowed_extensions = {".py"}

    match_path = Path(match_path)
    async for _ in awatch(match_path, watch_filter=PythonFilter()):
        disconnected = []
        for client in _clients:
            try:
                await client.send_text("reload")
            except Exception:
                disconnected.append(client)
        for client in disconnected:
            _clients.remove(client)


async def _hot_reload_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    _clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in _clients:
            _clients.remove(websocket)


def register_dev_reload(app: FastAPI) -> None:
    app.add_websocket_route("/hot-reload", _hot_reload_ws, name="hot-reload")
    app.add_middleware(SwaggerHotReloadMiddleware)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        task = asyncio.create_task(_watch_files())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    app.router.lifespan_context = lifespan