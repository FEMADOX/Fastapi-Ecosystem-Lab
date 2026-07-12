from learn_fastapi.src.users.application.queries import (
    GetUserByEmailQuery,
    GetUserByIdQuery,
)
from learn_fastapi.src.users.domain.entities import User as UserDomain
from learn_fastapi.src.users.domain.errors import UserDoesntExistError
from learn_fastapi.src.users.domain.ports import UsersRepository


class BaseUseCase:
    """Base class for all use cases."""

    def __init__(self, user_repository: UsersRepository) -> None:
        """Initialize the use case with the user repository."""
        self.user_repository = user_repository


class GetUserByIdUseCase(BaseUseCase):
    """Use case for retrieving a user by its ID."""

    async def execute(self, query: GetUserByIdQuery) -> UserDomain:
        """Execute the use case.

        Returns:
            The requested user.

        Raises:
            UserDoesntExistError: If the user doesn't exist.

        """
        user = await self.user_repository.get_user_by_id(query.user_id)
        if not user:
            raise UserDoesntExistError
        return user


class GetUserByEmailUseCase(BaseUseCase):
    """Use case for retrieving a user by its email."""

    async def execute(self, query: GetUserByEmailQuery) -> UserDomain:
        """Execute the use case.

        Returns:
            The requested user.

        Raises:
            UserDoesntExistError: If the user doesn't exist.

        """
        user = await self.user_repository.get_user_by_email(query.user_email)
        if not user:
            raise UserDoesntExistError
        return user
