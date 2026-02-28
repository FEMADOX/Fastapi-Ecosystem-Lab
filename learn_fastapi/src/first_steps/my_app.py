from fastapi import FastAPI

from learn_fastapi.src.config import lifespan

from .router import router

app = FastAPI(lifespan=lifespan)
# register_dev_reload(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


app.include_router(router)
