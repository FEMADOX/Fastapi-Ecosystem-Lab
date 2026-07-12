from learn_fastapi.src.auth.presentation.router import router as auth_router
from learn_fastapi.src.items.presentation.router import router as items_router
from learn_fastapi.src.sse.router import router as sse_router
from learn_fastapi.src.users.presentation.router import router as users_router

__all__ = [auth_router, items_router, sse_router, users_router]
