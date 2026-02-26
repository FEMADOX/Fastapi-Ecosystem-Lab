from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.staticfiles import StaticFiles

if TYPE_CHECKING:
    from fastapi import FastAPI


def mount_static_files(app: FastAPI) -> None:
    assets_dir = Path(__file__).parent / "static"
    images_dir = assets_dir / "images"

    images_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=assets_dir), name="static")
