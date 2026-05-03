import uvicorn
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_versionizer.versionizer import Versionizer, api_version
from sqlalchemy.exc import DBAPIError

from learn_fastapi.src.config import settings
from learn_fastapi.src.index import (
    auth_router,
    items_router,
    sse_router,
    users_router,
)
from learn_fastapi.src.lifespan import lifespan
from learn_fastapi.src.middleware import CorsMiddlewareConfigurer
from learn_fastapi.src.utils.alembic import app_logger

app = FastAPI(
    lifespan=lifespan,
    title="Learn FastAPI",
    version="1.0.0",
    root_path="/api",
)
# register_dev_reload(app)
CorsMiddlewareConfigurer(settings.allowed_hosts).add_middleware(app)


@app.exception_handler(DBAPIError)
def dbapi_error_handler(request: Request, exc: DBAPIError) -> JSONResponse:
    app_logger.error(f"Database error in {request.url.path}: {exc}")
    return JSONResponse(
        status_code=503, content={"detail": "Database temporarily unavailable"}
    )


@api_version(1)
@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


router = APIRouter()
router.include_router(auth_router)
router.include_router(items_router)
router.include_router(sse_router)
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
        host="0.0.0.0",  # noqa: S104
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()
