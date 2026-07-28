from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.application.use_cases import (
    CreateBaseItemsUseCase,
    CreateItemWithImageUseCase,
    DeleteItemUseCaseBase,
    GetItemUseCase,
    GetOwnerItemUseCase,
    ListItemsUseCase,
    ListOwnerItemsUseCase,
    PatchItemUseCaseBase,
    UpdateBaseItemsUseCase,
    UpdateItemImageUseCase,
)
from learn_fastapi.src.items.infrastructure.cache import RedisItemCache
from learn_fastapi.src.items.infrastructure.events import SSEItemEventPublisher
from learn_fastapi.src.items.infrastructure.image_storage import CloudinaryImageStorage
from learn_fastapi.src.items.infrastructure.repository import SQLAlchemyItemsRepository


@dataclass(frozen=True, slots=True)
class ItemsUseCases:
    """Application use cases required by the items router."""

    list_items: ListItemsUseCase
    get_item: GetItemUseCase
    list_owner_items: ListOwnerItemsUseCase
    get_owner_item: GetOwnerItemUseCase
    create_item: CreateBaseItemsUseCase
    update_item: UpdateBaseItemsUseCase
    patch_item: PatchItemUseCaseBase
    delete_item: DeleteItemUseCaseBase
    create_item_with_image: CreateItemWithImageUseCase
    update_item_image: UpdateItemImageUseCase


def get_items_use_cases(session: AsyncSessionDep) -> ItemsUseCases:
    repo = SQLAlchemyItemsRepository(session)
    image_storage = CloudinaryImageStorage()
    cache = RedisItemCache()
    event_publisher = SSEItemEventPublisher()

    base = repo, cache
    with_event = *base, event_publisher
    with_image = *with_event, image_storage

    return ItemsUseCases(
        list_items=ListItemsUseCase(*base),
        get_item=GetItemUseCase(*base),
        list_owner_items=ListOwnerItemsUseCase(*base),
        get_owner_item=GetOwnerItemUseCase(*base),
        create_item=CreateBaseItemsUseCase(*with_event),
        update_item=UpdateBaseItemsUseCase(*with_event),
        patch_item=PatchItemUseCaseBase(*with_event),
        delete_item=DeleteItemUseCaseBase(*with_event),
        create_item_with_image=CreateItemWithImageUseCase(*with_image),
        update_item_image=UpdateItemImageUseCase(*with_image),
    )


ItemsUseCasesDep = Annotated[ItemsUseCases, Depends(get_items_use_cases)]
