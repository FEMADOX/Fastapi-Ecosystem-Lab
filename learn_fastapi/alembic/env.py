import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Import all models so Alembic can detect them
from learn_fastapi.src.auth.models import User  # noqa: F401
from learn_fastapi.src.config import settings

# Import the Base class and all models for autogenerate support
from learn_fastapi.src.database import Base
from learn_fastapi.src.items.models import Item  # noqa: F401

DATABASE_URL = settings.database_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    # Keep already configured app/server loggers (e.g. uvicorn.access) enabled.
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Set the target metadata for autogenerate support
target_metadata = Base.metadata


# Get the database URL from environment variable or config
def get_sqlalchemy_url() -> str:
    """Get database URL from environment or config file.

    Returns:
        The database URL as a string.

    """
    env_url = DATABASE_URL
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
    connect_args = {}
    render_as_batch = False
    if url.startswith("sqlite"):
        # Enable foreign keys in SQLite
        connect_args = {"check_same_thread": False}
        render_as_batch = True

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_server_default=True,
        # SQLite-specific: enable batch mode for better ALTER support
        render_as_batch=render_as_batch,
        connect_args=connect_args,
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

        # SQLite-specific configuration
        connect_args = {}
        if url.startswith("sqlite"):
            # Enable foreign keys in SQLite
            connect_args = {"check_same_thread": False}

        connectable = create_async_engine(
            url,
            poolclass=pool.NullPool,
            echo=False,
            connect_args=connect_args,
        )

        async with connectable.begin() as connection:
            await connection.run_sync(_run_migrations)

        await connectable.dispose()

    asyncio.run(async_run())


def _run_migrations(connection: Connection) -> None:
    """Sync wrapper for running migrations with connection."""
    url = get_sqlalchemy_url()
    render_as_batch = url.startswith("sqlite")
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_server_default=True,
        render_as_batch=render_as_batch,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
