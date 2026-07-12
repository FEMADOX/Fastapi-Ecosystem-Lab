from typing import Annotated

from fastapi import Depends

from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.items.service import ItemService


def get_item_service(session: AsyncSessionDep) -> ItemService:
    return ItemService(session)


ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
