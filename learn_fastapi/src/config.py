import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from alembic import command
from alembic.config import Config
from fastapi.staticfiles import StaticFiles
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.websockets import WebSocket, WebSocketDisconnect
from watchfiles import awatch

from learn_fastapi.src.constants import (
    IMAGES_DIR,
    PROJECT_DIR,
    STATIC_DIR,
)
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
            except WebSocketDisconnect:
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


async def run_db_migrations() -> None:
    """Run Alembic migrations asynchronously using subprocess.

    This approach avoids import conflicts with local alembic directory.
    subprocess is safe here: we use list (not shell=True) with no user input.

    Raises:
        RuntimeError: If migration process fails.

    """
    # Import here to avoid conflicts with local alembic/ directory

    alembic_cfg = Config(PROJECT_DIR / "alembic.ini")

    try:
        await asyncio.to_thread(lambda: command.upgrade(alembic_cfg, "head"))
    except Exception as e:
        msg = f"Migration failed: {e!s}"
        raise RuntimeError(msg) from e


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    mount_static_files(app)
    await run_db_migrations()
    task = asyncio.create_task(_watch_files())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


class Settings(BaseSettings):
    secret_key: SecretStr
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()  # ty:ignore[missing-argument]
