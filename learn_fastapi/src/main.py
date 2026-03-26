import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi_versionizer.versionizer import Versionizer, api_version

from learn_fastapi.src.auth.router import router as auth_router
from learn_fastapi.src.config import lifespan, settings
from learn_fastapi.src.items.router import router as items_router
from learn_fastapi.src.middleware import CorsMiddlewareConfigurer
from learn_fastapi.src.users.router import router as users_router

app = FastAPI(
    lifespan=lifespan,
    title="Learn FastAPI",
    version="1.0.0",
    root_path="/api",
)
# register_dev_reload(app)
CorsMiddlewareConfigurer(settings.allowed_hosts).add_middleware(app)


@api_version(1)
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


router = APIRouter()
router.include_router(items_router)
router.include_router(auth_router)
router.include_router(users_router)

app.include_router(router)

versions = Versionizer(
    app=app,
    prefix_format="/v{major}",
    semantic_version_format="{major}",
    latest_prefix="/latest",
    sort_routes=True,
).versionize()


def main() -> None:
    uvicorn.run(
        "learn_fastapi.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
