import asyncio
import uuid
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.params import Path as PathParam
from starlette.status import HTTP_404_NOT_FOUND

from learn_fastapi.src.constants import DB
from learn_fastapi.src.database import save_db
from learn_fastapi.src.first_steps.annotations import (
    ImageCaption,
    ImageFile,
    ImageFileOptional,
    ItemDescription,
    ItemName,
    ItemPrice,
    ItemTax,
)
from learn_fastapi.src.first_steps.schema import Image, Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
def read_items() -> dict[str, Item]:
    return DB


@router.get("/{id_param}")
async def read_item(id_param: int) -> Item:
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


async def save_image_file(
    image_file: UploadFile, caption: str = "No description provided"
) -> Image:
    """Save the image to disk and return an Image Model.

    Raises:
        HTTPException: If the image file does not have a filename.

    Returns:
        Image: The saved image model.

    """
    image_dir = Path(__file__).parent.parent / "static" / "images"

    if not image_file.filename:
        raise HTTPException(status_code=422, detail="Image file must have a filename")

    await asyncio.to_thread(image_dir.mkdir, parents=True, exist_ok=True)
    file_path = image_dir / image_file.filename

    if not file_path.exists():
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await image_file.read())

    return Image(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=f"/static/images/{image_file.filename}",
    )


@router.post("/image")
async def submit_an_item_image(
    image_file: ImageFile,
    caption: ImageCaption = "No description provided",
) -> Image:
    return await save_image_file(image_file, caption)


@router.post("/with-image/")
async def create_item_with_image(
    name: ItemName = "Default Item",
    description: ItemDescription = "No description provided",
    price: ItemPrice = 0.00,
    tax: ItemTax = 0.00,
    image_file: ImageFileOptional = None,
    caption: ImageCaption = "No description provided",
) -> Item:
    item = Item(
        name=name,
        description=description,
        price=price,
        tax=tax,
    )
    if image_file:
        image = await save_image_file(image_file, caption)
        item.image_url = image.url

    item_id = uuid.uuid4()
    DB[str(item_id)] = item
    save_db(DB)
    return item
