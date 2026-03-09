import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from learn_fastapi.src.config import settings

# Import the Base class and all models for autogenerate support
from learn_fastapi.src.database import Base

DATABASE_URL = settings.database_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata


# Get the database URL from environment variable or config
def get_sqlalchemy_url() -> str:
    """Get database URL from environment or config file.

    Returns:
        The database URL as a string.

    """
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url
    return config.get_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_sqlalchemy_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    async def async_run() -> None:
        url = get_sqlalchemy_url()

        connectable = create_async_engine(
            url,
            poolclass=pool.NullPool,
            echo=False,
        )

        async with connectable.begin() as connection:
            await connection.run_sync(_run_migrations)

        await connectable.dispose()

    asyncio.run(async_run())


def _run_migrations(connection: Connection) -> None:
    """Sync wrapper for running migrations with connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
