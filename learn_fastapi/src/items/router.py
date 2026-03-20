import asyncio
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi_versionizer.versionizer import api_version
from starlette.status import HTTP_200_OK

from learn_fastapi.src.constants import IMAGES_DIR
from learn_fastapi.src.utils.dependencies import CurrentUserDep

from .annotations import (
    ImageCaption,
    ImageFile,
    ImageFilename,
    ImageFileOptional,
    ItemDescription,
    ItemName,
    ItemPrice,
    ItemTax,
)
from .dependencies import ItemServiceDep
from .exceptions import image_not_found_exception
from .schema import (
    ItemSchema,
    ItemUpdateSchema,
)

router = APIRouter(prefix="/items", tags=["items"])


@api_version(1)
@router.get("/")
async def read_items(service: ItemServiceDep) -> list[ItemSchema]:
    """Return all items stored in the database.

    Args:
        service: Injected ItemService dependency.

    Returns:
        A list of all ItemSchema objects (maybe empty).

    """
    return await service.get_all_items()


@api_version(1)
@router.get("/{id_param}")
async def read_item(id_param: UUID, service: ItemServiceDep) -> ItemSchema:
    """Return a single item by its UUID.

    Args:
        id_param: UUID of the item to retrieve.
        service: Injected ItemService dependency.

    Returns:
        The matching ItemSchema.

    """
    return await service.get_item(id_param)


@api_version(1)
@router.post("/")
async def create_item(
    item: ItemUpdateSchema, service: ItemServiceDep, current_user: CurrentUserDep
) -> ItemSchema:
    """Create a new item owned by the authenticated user.

    Args:
        item: Validated item payload.
        service: Injected ItemService dependency.
        current_user: The authenticated user who will own the item.

    Returns:
        The newly created ItemSchema.

    """
    return await service.create_item(item, current_user)


@api_version(1)
@router.put("/{id_param}")
async def update_item(
    id_param: UUID,
    item_param: ItemUpdateSchema,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
) -> ItemSchema:
    """Replace all fields of an item owned by the authenticated user.

    All fields are written, including those omitted from the request body
    (which receive their schema default values).

    Args:
        id_param: UUID of the item to update.
        item_param: Complete field values for the item.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.

    Returns:
        The updated ItemSchema.

    """
    return await service.update_item(id_param, item_param, current_user)


@api_version(1)
@router.patch("/{id_param}")
async def patch_item(
    id_param: UUID,
    item_param: ItemUpdateSchema,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
) -> ItemSchema:
    """Apply a partial update to an item owned by the authenticated user.

    Only fields explicitly included in the request body are modified;
    omitted fields retain their current values.

    Args:
        id_param: UUID of the item to update.
        item_param: Partial field values to apply.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.

    Returns:
        The updated ItemSchema.

    """
    return await service.patch_item(id_param, item_param, current_user)


@api_version(1)
@router.delete("/{id_param}")
async def delete_item(
    id_param: UUID, service: ItemServiceDep, current_user: CurrentUserDep
) -> dict[str, str | int]:
    """Delete an item owned by the authenticated user.

    Args:
        id_param: UUID of the item to delete.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.

    Returns:
        Confirmation message with HTTP 200 status code.

    """
    await service.delete_item(id_param, current_user)
    return {"detail": "Item deleted successfully", "status_code": HTTP_200_OK}


@api_version(1)
@router.post("/image/{id_param}")
async def submit_an_item_image(
    id_param: UUID,
    service: ItemServiceDep,
    image_file: ImageFile,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    """Upload an image and attach it to an existing item.

    Args:
        id_param: UUID of the target item.
        service: Injected ItemService dependency.
        image_file: Image file to upload (multipart/form-data).
        caption: Optional alt-text or description for the image.

    Returns:
        The updated item with its new ``image_url``.

    """
    return await service.update_item_image(id_param, image_file, caption)


@api_version(1)
@router.get("/image/")
async def get_image(filename: ImageFilename) -> FileResponse:
    """Serve a stored image file by its base filename (without extension).

    Performs a glob search in ``IMAGES_DIR`` for any file whose stem matches
    the supplied name, then streams it back with the correct media type.

    Args:
        filename: Base name of the image, without file extension.

    Returns:
        The image file as a ``FileResponse`` with the appropriate media type.

    Raises:
        image_not_found_exception: 404 if no matching image file is found.

    """
    matches = await asyncio.to_thread(lambda: list(IMAGES_DIR.glob(f"{filename}.*")))
    if not matches:
        raise image_not_found_exception()

    file_path = matches[0]
    return FileResponse(
        path=file_path,
        media_type=f"image/{file_path.suffix.lstrip('.')}",
        filename=filename,
    )


@api_version(1)
@router.post("/with-image/")
async def create_item_with_image(  # noqa: PLR0913, PLR0917
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    name: ItemName,
    description: ItemDescription = "No description provided",
    price: ItemPrice = 0.00,
    tax: ItemTax = 0.00,
    image_file: ImageFileOptional = None,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    """Create an item with an optional image in a single multipart request.

    Validates that no other item shares the same name before creation.
    If an image file is supplied it is saved to disk and its URL stored on
    the newly created item.

    Args:
        service: Injected ItemService dependency.
        current_user: The authenticated user who will own the item.
        name: Display name for the item (must be unique).
        description: Human-readable description.
        price: Base price.
        tax: Tax rate.
        image_file: Optional image to attach.
        caption: Alt-text for the image.

    Returns:
        The newly created ItemSchema, with ``image_url`` set when an image
        was provided.

    """
    return await service.create_item_with_image(
        name=name,
        description=description,
        price=price,
        tax=tax,
        owner=current_user,
        image_file=image_file,
        caption=caption,
    )
