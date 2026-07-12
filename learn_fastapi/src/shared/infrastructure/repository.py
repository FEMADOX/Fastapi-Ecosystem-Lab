from sqlalchemy.ext.asyncio import AsyncSession


class BaseSQLAlchemyRepository:
    """Repository for managing apps using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with an asynchronous SQLAlchemy session."""
        self.session = session

    async def commit(self) -> None:
        """Commit the current unit of work."""
        await self.session.commit()
