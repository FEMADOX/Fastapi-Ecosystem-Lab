import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from fastapi.staticfiles import StaticFiles
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    IMAGES_DIR,
    MEDIA_DIR,
    PROJECT_DIR,
    STATIC_DIR,
)
from .middleware import SwaggerHotReloadMiddleware
from .utils.alembic import check_pending_migrations
from .utils.hot_reload import _hot_reload_ws, _watch_files

if TYPE_CHECKING:
    from fastapi import FastAPI


def mount_static_files(app: FastAPI) -> None:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


def register_dev_reload(app: FastAPI) -> None:
    app.add_middleware(SwaggerHotReloadMiddleware)  # ty:ignore[invalid-argument-type]
    app.add_websocket_route("/hot-reload", _hot_reload_ws, name="hot-reload")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    mount_static_files(app)
    await check_pending_migrations()
    task = asyncio.create_task(_watch_files())
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


class Settings(BaseSettings):
    secret_key: SecretStr
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"  # noqa: S105
    postgres_db: str = "learn_fastapi"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    database_url: str

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()  # ty:ignore[missing-argument]
