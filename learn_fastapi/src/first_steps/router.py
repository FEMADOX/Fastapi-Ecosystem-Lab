import asyncio
from uuid import UUID

import aiofiles
from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select, update
from starlette.status import HTTP_200_OK, HTTP_404_NOT_FOUND

from learn_fastapi.src.constants import IMAGES_DIR
from learn_fastapi.src.database import AsyncSessionDep
from learn_fastapi.src.first_steps.annotations import (
    ImageCaption,
    ImageFile,
    ImageFilename,
    ImageFileOptional,
    ItemDescription,
    ItemName,
    ItemPrice,
    ItemTax,
)
from learn_fastapi.src.first_steps.models import Item as ItemModel
from learn_fastapi.src.first_steps.schema import Image, Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/")
async def read_items(
    session: AsyncSessionDep, offset: int = 0, limit: int = 10
) -> list[Item]:
    list_items = await session.execute(select(ItemModel).offset(offset).limit(limit))
    return list_items.scalars().all()


@router.get("/{id_param}")
async def read_item(id_param: UUID, session: AsyncSessionDep) -> Item:
    item = await session.get(ItemModel, id_param)
    if item is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("/")
async def create_item(item: Item, session: AsyncSessionDep) -> Item:
    item_db = ItemModel(**item.model_dump(exclude={"id"}))
    session.add(item_db)
    await session.commit()
    await session.refresh(item_db)
    return item


@router.put("/{id_param}")
async def update_item(id_param: UUID, session: AsyncSessionDep, item: Item) -> Item:
    item_db = await session.get(ItemModel, id_param)
    if item_db is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")

    item_data = item.model_dump(exclude_unset=True, exclude={"id"})
    await session.execute(
        update(ItemModel).where(ItemModel.id == item_db.id).values(**item_data)
    )
    await session.commit()
    await session.refresh(item_db)
    return item_db


@router.delete("/{id_param}")
async def delete_item(id_param: UUID, session: AsyncSessionDep) -> dict[str, str | int]:
    item = await session.get(ItemModel, id_param)
    if item is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")
    await session.delete(item)
    await session.commit()
    return {"detail": "Item deleted successfully", "status_code": HTTP_200_OK}


async def save_image_file(
    image_file: UploadFile, caption: str = "No description provided"
) -> Image:
    """Save the image to disk and return an Image Model.

    Raises:
        HTTPException: If the image file does not have a filename.

    Returns:
        Image: The saved image model.

    """
    if not image_file.filename:
        raise HTTPException(status_code=422, detail="Image file must have a filename")

    await asyncio.to_thread(IMAGES_DIR.mkdir, parents=True, exist_ok=True)
    file_path = IMAGES_DIR / image_file.filename

    if not file_path.exists():
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await image_file.read())

    return Image(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=f"/static/images/{image_file.filename}",
    )


@router.post("/image/{id_param}")
async def submit_an_item_image(
    id_param: UUID,
    session: AsyncSessionDep,
    image_file: ImageFile,
    caption: ImageCaption = "No description provided",
) -> Item:
    item_db = await session.get(ItemModel, id_param)

    if item_db is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Item not found")

    image_file = await save_image_file(image_file, caption)
    await session.execute(
        update(ItemModel)
        .where(ItemModel.id == item_db.id)
        .values(image_url=image_file.url)
    )
    await session.commit()
    await session.refresh(item_db)
    return item_db


@router.get("/image/")
async def get_image(filename: ImageFilename) -> FileResponse:
    matches = await asyncio.to_thread(lambda: list(IMAGES_DIR.glob(f"{filename}.*")))
    if not matches:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Image not found")

    file_path = matches[0]

    return FileResponse(
        path=file_path,
        media_type=f"image/{file_path.suffix.lstrip('.')}",
        filename=filename,
    )


@router.post("/with-image/")
async def create_item_with_image(  # noqa: PLR0913, PLR0917
    session: AsyncSessionDep,
    name: ItemName = "Default Item",
    description: ItemDescription = "No description provided",
    price: ItemPrice = 0.00,
    tax: ItemTax = 0.00,
    image_file: ImageFileOptional = None,
    caption: ImageCaption = "No description provided",
) -> Item:
    result = await session.execute(select(ItemModel).where(ItemModel.name == name))
    result = result.scalar_one_or_none()
    if result is not None:
        raise HTTPException(
            status_code=422, detail=f"An item with name '{name}' already exists"
        )

    item_db = ItemModel(
        name=name,
        description=description,
        price=price,
        tax=tax,
    )
    if image_file:
        image = await save_image_file(image_file, caption)
        item_db.image_url = image.url

    session.add(item_db)
    await session.commit()
    await session.refresh(item_db)
    return item_db
