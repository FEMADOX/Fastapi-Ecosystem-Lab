from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from learn_fastapi.src.config import settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# Configuración específica para SQLite
connect_args = {}
if settings.database_url.startswith("sqlite"):
    # Para SQLite: permitir acceso desde múltiples threads
    # English:
    connect_args = {"check_same_thread": False, "timeout": 1500}

engine = create_async_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,  # Cambiar a True para debug
)


AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except DBAPIError:
            await session.rollback()
            raise


AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]
