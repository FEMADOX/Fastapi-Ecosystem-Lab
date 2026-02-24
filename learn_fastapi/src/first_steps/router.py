import asyncio
import uuid
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.params import Path as PathParam
from starlette.status import HTTP_404_NOT_FOUND

from learn_fastapi.src.constants import DB
from learn_fastapi.src.database import save_db
from learn_fastapi.src.first_steps.schema import Image, Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/hello-world/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


@router.get("/")
def read_items() -> dict[str, Item]:
    return DB


@router.get("/{id_param}")
async def read_item(id_param: Annotated[int, PathParam(lt=4)]) -> Item:
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


@router.post("/image")
async def submit_an_item_image(
    image_file: Annotated[UploadFile, File(description="The image file to upload")],
    caption: Annotated[
        str, Form(description="The caption for the image")
    ] = "No description provided",
) -> Image:
    # Absolute path relative to this file: learn_fastapi/src/assets/images/
    image_dir = Path(__file__).parent.parent / "assets" / "images"

    # Download the image file and save it to disk (assets/images/)
    if image_file and image_file.filename:
        await asyncio.to_thread(image_dir.mkdir, parents=True, exist_ok=True)
        file_path = image_dir / image_file.filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await image_file.read())

    # Return the image information as a response
    return Image(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=f"/assets/images/{image_file.filename}",
    )


# @router.post("/with-image/")
# async def create_item_with_image(
#     item_data: Annotated[
#         str, Form(description="The item data as a JSON string")
#     ] = """{"name": "Default Item", "description": "This is a default item", "price": 0.00, "tax": 0.00}""",
#     image_file: Annotated[
#         UploadFile | None, File(description="Optional image for the item")
#     ] = None,
#     caption: Annotated[
#         str, Form(description="Image description")
#     ] = "No description provided",
# ) -> Item:
#     try:
#         item = Item.model_validate_json(item_data)
#     except ValueError as error:
#         raise HTTPException(status_code=422, detail=f"Invalid item data:) {error}")
#
#     if image_file:
#         item.image = Image(
#             image=image_file,
#             name=image_file.filename,
#             description=caption,
#         )
#
#     item_id = uuid.uuid4()
#     DB[str(item_id)] = item
#     save_db(DB)
#     return item
