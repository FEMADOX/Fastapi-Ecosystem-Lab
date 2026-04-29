import asyncio
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

from fastapi.staticfiles import StaticFiles

from learn_fastapi.src import database
from learn_fastapi.src.cache.redis_client import close_redis

from .cache.redis_client import check_redis_health
from .constants import (
    IMAGES_DIR,
    MEDIA_DIR,
    STATIC_DIR,
)
from .middleware import SwaggerHotReloadMiddleware
from .utils.alembic import check_pending_migrations
from .utils.hot_reload import hot_reload_ws, watch_files

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI


def mount_static_files(app: FastAPI) -> None:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


def register_dev_reload(app: FastAPI) -> None:
    app.add_middleware(SwaggerHotReloadMiddleware)
    app.add_api_websocket_route("/hot-reload", hot_reload_ws, name="hot-reload")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    mount_static_files(app)
    startup_tasks = [
        asyncio.create_task(check_pending_migrations()),
        asyncio.create_task(check_redis_health()),
    ]
    task = asyncio.create_task(watch_files())
    try:
        yield
    finally:
        for startup_task in startup_tasks:
            if not startup_task.done():
                startup_task.cancel()

        if startup_tasks:
            with suppress(asyncio.CancelledError):
                await asyncio.gather(*startup_tasks, return_exceptions=True)

        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        await close_redis()

        await database.engine.dispose()
