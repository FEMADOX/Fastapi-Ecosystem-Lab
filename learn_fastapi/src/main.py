from fastapi import APIRouter, FastAPI

from learn_fastapi.src.auth.router import router as auth_router
from learn_fastapi.src.config import lifespan
from learn_fastapi.src.items.router import router as items_router
from learn_fastapi.src.users.router import router as users_router

API_PREFIX = "/api/v1"

app = FastAPI(
    lifespan=lifespan,
    title="Learn FastAPI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)
# register_dev_reload(app)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


versioned_router = APIRouter(prefix=API_PREFIX)
versioned_router.add_api_route("/", root, methods=["GET"], tags=["root"])
versioned_router.include_router(items_router, prefix="/items", tags=["items"])
versioned_router.include_router(auth_router, prefix="/auth", tags=["auth"])
versioned_router.include_router(users_router, prefix="/users", tags=["users"])

app.include_router(versioned_router)


def main() -> None:
    import uvicorn

    uvicorn.run(
        "learn_fastapi.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_delay=0,
    )

if __name__ == "__main__":
    main()
