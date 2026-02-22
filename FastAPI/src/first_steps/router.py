import uuid

from starlette.status import HTTP_404_NOT_FOUND

from fastapi import APIRouter, HTTPException
from FastAPI.src.constants import DB
from FastAPI.src.database import save_db
from FastAPI.src.first_steps.schema import Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/hello-world/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/")
def read_items() -> dict[str, Item]:
    return DB


@router.get("/{id_param}")
async def read_item(id_param: int | uuid.UUID) -> Item:
    item = DB.get(str(id_param))
    if item is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("/")
async def create_item(item: Item) -> Item:
    item_id = uuid.uuid4()
    DB[str(item_id)] = item
    save_db(DB)
    return item


@router.put("/{id_param}")
async def update_item(id_param: int | uuid.UUID, item: Item) -> Item:
    item_id = id_param
    DB[str(item_id)] = item
    save_db(DB)
    return item


@router.delete("/{id_param}")
async def delete_item(id_param: int | uuid.UUID) -> Item:
    item_id = id_param
    item = DB.pop(str(item_id), None)
    if item is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    save_db(DB)
    return item
