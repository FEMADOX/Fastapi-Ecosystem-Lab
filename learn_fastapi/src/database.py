from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/learn_fastapi"

engine = create_async_engine(POSTGRES_URL)

AsyncSessionMaker = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionMaker() as session:
        yield session


AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
