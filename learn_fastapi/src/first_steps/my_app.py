from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .router import router
from ..middleware import register_dev_reload

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


app.include_router(router)
register_dev_reload(app)

# Mount StaticFiles
assets_dir = Path(__file__).parent.parent / "static"
images_dir = assets_dir / "images"

images_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=assets_dir), name="static")
