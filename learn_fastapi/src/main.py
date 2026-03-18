from fastapi import FastAPI

from learn_fastapi.src.auth.router import router as auth_router
from learn_fastapi.src.config import lifespan
from learn_fastapi.src.items.router import router as items_router
from learn_fastapi.src.users.router import router as users_router

app = FastAPI(
    lifespan=lifespan,
    title="Learn FastAPI",
    version="1.0.0",
    root_path="/api/v1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
# register_dev_reload(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


app.add_api_route("/", root, methods=["GET"], tags=["root"])
app.include_router(items_router, prefix="/items", tags=["items"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(users_router, prefix="/users", tags=["users"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        reload=True,
        reload_delay=0,
    )
