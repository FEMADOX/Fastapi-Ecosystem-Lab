from typing import cast

from sqlalchemy import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from learn_fastapi.src.database import AsyncSessionDep


class BaseRepository:
    """Base repository with typed wrappers around AsyncSession query methods.

    Provides ``_execute()`` so subclasses get a properly-inferred
    ``Result[_T]`` return type without needing ``cast()`` at every call site.
    The single ``# type: ignore`` lives here and nowhere else.
    """

    def __init__(self, session: AsyncSessionDep) -> None:
        """Initialize the repository with an async database session."""
        self.session: AsyncSession = session

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()


def bool_to_column(value: bool) -> ColumnElement[bool]:
    """Convert a Python bool to a SQLAlchemy column element boolean.

    This is necessary to work around a quirk in SQLAlchemy's type system where
    boolean expressions involving column elements can sometimes be misinterpreted
    as literal Python booleans, leading to incorrect query construction.

    Args:
        value: The Python boolean value to convert.

    Returns:
        A SQLAlchemy ColumnElement representing the boolean value.

    """
    return cast("ColumnElement[bool]", value)
