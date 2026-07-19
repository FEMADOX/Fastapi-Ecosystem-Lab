from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.application.use_cases import (
    CreateItemUseCase,
    CreateItemWithImageUseCase,
    DeleteItemUseCase,
    GetItemUseCase,
    GetOwnerItemUseCase,
    ListItemsUseCase,
    ListOwnerItemsUseCase,
    PatchItemUseCase,
    UpdateItemImageUseCase,
    UpdateItemUseCase,
)
from learn_fastapi.src.items.infrastructure.image_storage import CloudinaryImageStorage
from learn_fastapi.src.items.infrastructure.repository import SQLAlchemyItemsRepository
from learn_fastapi.src.items.service import ItemsService, ItemsUseCases
from learn_fastapi.src.users.application.use_cases import GetUserByIdUseCase
from learn_fastapi.src.users.infrastructure.repository import SQLAlchemyUsersRepository


def get_items_service(session: AsyncSessionDep) -> ItemsService:
    """Build an ``ItemsService`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``AuthService`` instance.

    """
    clean_users_repository = SQLAlchemyUsersRepository(session)
    clean_items_repository = SQLAlchemyItemsRepository(session)
    image_storage = CloudinaryImageStorage()

    return ItemsService(
        ItemsUseCases(
            GetUserByIdUseCase(clean_users_repository),
            ListItemsUseCase(clean_items_repository),
            GetItemUseCase(clean_items_repository),
            ListOwnerItemsUseCase(clean_items_repository),
            GetOwnerItemUseCase(clean_items_repository),
            CreateItemUseCase(clean_items_repository),
            UpdateItemUseCase(clean_items_repository),
            PatchItemUseCase(clean_items_repository),
            DeleteItemUseCase(clean_items_repository),
            CreateItemWithImageUseCase(clean_items_repository, image_storage),
            UpdateItemImageUseCase(clean_items_repository, image_storage),
        )
    )


ItemsServiceDep = Annotated[ItemsService, Depends(get_items_service)]
