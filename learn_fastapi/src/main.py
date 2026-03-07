from fastapi import FastAPI

from learn_fastapi.src.auth.router import router as auth_router
from learn_fastapi.src.config import lifespan, register_dev_reload
from learn_fastapi.src.items.router import router as items_router

app = FastAPI(lifespan=lifespan)
register_dev_reload(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


app.include_router(items_router, prefix="/items", tags=["items"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        reload_delay=0,
    )
