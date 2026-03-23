import logging
from typing import TYPE_CHECKING

from alembic import migration, script
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from learn_fastapi.src.constants import PROJECT_DIR

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.ext.asyncio import AsyncConnection

app_logger = logging.getLogger("uvicorn.error")


async def _is_database_at_head(
    connection: AsyncConnection, alembic_script_dir: ScriptDirectory
) -> bool:
    """Check if DB heads are equal to script heads (cookbook approach).

    Args:
        connection: Engine async connection
        alembic_script_dir: The alembic.ini script directory

    Returns:
        True if DB is at head, False otherwise.

    """

    def _check(sync_connection: Connection) -> bool:
        context = migration.MigrationContext.configure(sync_connection)
        return set(context.get_current_heads()) == set(alembic_script_dir.get_heads())

    return await connection.run_sync(_check)


async def _is_there_any_model_change(
    connection: AsyncConnection, alembic_script_dir: ScriptDirectory
) -> bool:
    """Check if project models has been changed.

    Check if there is any kind of change in the project models without been committed
    with alembic for a proper migration.

    Args:
        connection: Engine async connection
        alembic_script_dir: The alembic.ini script directory

    Returns:
        True if there are changes without coverage, False otherwise.

    """
    from learn_fastapi.src.database import Base

    def _compare(sync_connection: Connection) -> list:
        # Build a MigrationContext that points at the live DB,
        # then diff it against your SQLAlchemy metadata.
        # This is exactly what `alembic check` does internally.
        context = MigrationContext.configure(
            sync_connection,
            opts={
                # Tell autogenerate which script directory to use
                # so it can resolve render_as_batch, naming conventions, etc.
                "script": alembic_script_dir,
            },
        )
        # Returns a list of Operation objects.
        # Empty list → no diff → models match DB.
        return compare_metadata(context, Base.metadata)

    diffs = await connection.run_sync(_compare)
    return len(diffs) > 0


async def check_pending_migrations() -> None:
    """Check if there are pending Alembic migrations."""
    from learn_fastapi.src.database import engine

    alembic_cfg = Config(str(PROJECT_DIR / "alembic.ini"))
    directory = script.ScriptDirectory.from_config(alembic_cfg)

    app_logger.info("Checking pending migrations")

    try:
        async with engine.begin() as conn:
            app_logger.info("Checking database revision against Alembic heads")
            is_head = await _is_database_at_head(conn, directory)
            if not is_head:
                app_logger.warning(
                    "DB is not at head -- run `alembic upgrade head` to update"
                )
                return

            app_logger.info("Database revision is already at head")

            app_logger.info(
                "Check if there are any changes in the models "
                "without been covered by a migration"
            )
            has_pending_changes = await _is_there_any_model_change(conn, directory)
            if has_pending_changes:
                app_logger.warning(
                    "Uncommitted model changes — run alembic revision --autogenerate"
                )
                return

            app_logger.info("Database and models are in sync")
    except Exception:
        app_logger.exception("Error while checking pending migrations:")
    finally:
        await engine.dispose()
    return
