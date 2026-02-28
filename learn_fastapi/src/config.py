import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from fastapi.staticfiles import StaticFiles
from starlette.websockets import WebSocket, WebSocketDisconnect
from watchfiles import awatch

from learn_fastapi.src.constants import IMAGES_DIR, STATIC_DIR
from learn_fastapi.src.database import create_db_and_tables
from learn_fastapi.src.middleware import SwaggerHotReloadMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI


async def _watch_files(match_path: str = ".") -> None:
    # async for _ in awatch(match_path, watch_filter=PythonFilter()):
    async for _ in awatch(match_path):
        disconnected = []
        for client in _clients:
            try:
                await client.send_text("reload")
            except Exception:
                disconnected.append(client)
        for client in disconnected:
            _clients.remove(client)


_clients: list[WebSocket] = []


def mount_static_files(app: FastAPI) -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


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
    app.add_middleware(SwaggerHotReloadMiddleware)  # ty:ignore[invalid-argument-type]
    app.add_websocket_route("/hot-reload", _hot_reload_ws, name="hot-reload")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    mount_static_files(app)
    await create_db_and_tables()
    task = asyncio.create_task(_watch_files())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task
