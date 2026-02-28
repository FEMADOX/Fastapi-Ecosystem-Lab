from typing import TYPE_CHECKING, Annotated

from fastapi import Depends
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///./{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_async_engine(sqlite_url, connect_args=connect_args)

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

# DB_PATH = Path(__file__).parent / "database.json"
#
#
# def load_db() -> dict[str, Item]:
#     with Path.open(DB_PATH) as f:
#         raw = json.load(f)
#         return {key: Item(**value) for key, value in raw.items()}
#
#
# def save_db(db: dict[str, Item]) -> None:
#     serializable = {}
#     for key, value in db.items():
#         if not isinstance(value, Item):
#             msg = f"Value for key {key} is not an instance of Item"
#             raise TypeError(msg)
#         serializable[key] = value.model_dump()
#
#     with Path.open(DB_PATH, "w") as f:
#         json.dump(serializable, f, indent=4)
