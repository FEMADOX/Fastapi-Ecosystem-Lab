from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/learn_fastapi"

engine = create_async_engine(POSTGRES_URL)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# Import all models here so they're registered with Base.metadata
# This is required for Alembic to detect changes
from learn_fastapi.src.auth.models import RefreshToken, User  # noqa: E402, F401
from learn_fastapi.src.items.models import Item  # noqa: E402, F401


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
