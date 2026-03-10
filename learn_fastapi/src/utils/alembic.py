import logging

from alembic import migration, script
from alembic.config import Config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from learn_fastapi.src import config
from learn_fastapi.src.constants import PROJECT_DIR

app_logger = logging.getLogger("uvicorn.error")
alembic_cfg = Config(str(PROJECT_DIR / "alembic.ini"))


async def _is_database_at_head() -> bool:
    """Check if DB heads are equal to script heads (cookbook approach).

    Returns:
        True if DB is at head, False otherwise.

    """
    database_url = config.settings.database_url
    directory = script.ScriptDirectory.from_config(alembic_cfg)

    connect_args = (
        {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    )
    engine = create_async_engine(database_url, connect_args=connect_args)
    try:
        async with engine.begin() as connection:

            def _check(sync_connection: Connection) -> bool:
                context = migration.MigrationContext.configure(sync_connection)
                return set(context.get_current_heads()) == set(directory.get_heads())

            return await connection.run_sync(_check)
    finally:
        await engine.dispose()


async def check_pending_migrations() -> bool:
    """Check if there are pending Alembic migrations.

    Returns:
        True if there are pending migrations, False otherwise.

    """
    app_logger.info("Checking database revision against Alembic heads")

    is_head = await _is_database_at_head()
    if is_head:
        app_logger.info("Database revision is already at head")
        return False
    app_logger.warning(
        "Database revision is not at head, you need to migrate to last revision"
    )
    return True
