from fastapi import FastAPI

from learn_fastapi.src.config import mount_static_files
from learn_fastapi.src.middleware import register_dev_reload

from .router import router

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


app.include_router(router)
register_dev_reload(app)
mount_static_files(app)
