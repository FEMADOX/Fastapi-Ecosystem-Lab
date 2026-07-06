from uuid import UUID

from fastapi import APIRouter, BackgroundTasks
from fastapi_versionizer.versionizer import api_version
from starlette.status import HTTP_204_NO_CONTENT

from learn_fastapi.src.items.cache import invalidate_items_namespace
from learn_fastapi.src.utils.dependencies import CurrentUserDep

from .annotations import (
    AnnotatedOwnerId,
    ImageCaption,
    ImageFile,
    ImageFileOptional,
    ItemDescription,
    ItemName,
    ItemPrice,
    ItemTax,
)
from .dependencies import ItemServiceDep
from .schema import (
    ItemPatchSchema,
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
    return await service.list_all_items()


@api_version(1)
@router.get("/owner")
async def read_owner_items(
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    owner_id: AnnotatedOwnerId = None,
) -> list[ItemSchema]:
    """Return items for the authenticated user or an admin-selected owner.

    Args:
        service: Injected ItemService dependency.
        current_user: Authenticated user making the request.
        owner_id: Optional owner UUID. Only superusers can target another owner.

    Returns:
        A list of ItemSchema objects for the effective owner.

    """
    owner = await service.resolve_owner(current_user, owner_id)
    return await service.list_user_items(owner)


@api_version(1)
@router.get("/owner/{id_param}")
async def read_owner_item(
    id_param: UUID,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    owner_id: AnnotatedOwnerId = None,
) -> ItemSchema:
    """Return one item for the authenticated user or an admin-selected owner.

    Args:
        id_param: UUID of the item to retrieve.
        service: Injected ItemService dependency.
        current_user: Authenticated user making the request.
        owner_id: Optional owner UUID. Only superusers can target another owner.

    Returns:
        The matching ItemSchema for the effective owner.

    """
    owner = await service.resolve_owner(current_user, owner_id)
    return await service.get_user_item(id_param, owner)


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
    item: ItemUpdateSchema,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> ItemSchema:
    """Create a new item owned by the authenticated user.

    Args:
        item: Validated item payload.
        service: Injected ItemService dependency.
        current_user: The authenticated user who will own the item.
        background_tasks: Background tasks manager.

    Returns:
        The newly created ItemSchema.

    """
    result = await service.create_item(item, current_user)
    background_tasks.add_task(invalidate_items_namespace)
    return result


@api_version(1)
@router.put("/{id_param}")
async def update_item(
    id_param: UUID,
    item_param: ItemUpdateSchema,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> ItemSchema:
    """Replace all fields of an item owned by the authenticated user.

    All fields are written, including those omitted from the request body
    (which receive their schema default values).

    Args:
        id_param: UUID of the item to update.
        item_param: Complete field values for the item.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.
        background_tasks: Background tasks manager.

    Returns:
        The updated ItemSchema.

    """
    result = await service.update_item(id_param, item_param, current_user)
    background_tasks.add_task(invalidate_items_namespace)
    return result


@api_version(1)
@router.patch("/{id_param}")
async def patch_item(
    id_param: UUID,
    item_param: ItemPatchSchema,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> ItemSchema:
    """Apply a partial update to an item owned by the authenticated user.

    Only fields explicitly included in the request body are modified;
    omitted fields retain their current values.

    Args:
        id_param: UUID of the item to update.
        item_param: Partial field values to apply.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.
        background_tasks: Background tasks manager.

    Returns:
        The updated ItemSchema.

    """
    result = await service.patch_item(id_param, item_param, current_user)
    background_tasks.add_task(invalidate_items_namespace)
    return result


@api_version(1)
@router.delete("/{id_param}")
async def delete_item(
    id_param: UUID,
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
) -> dict[str, str | int]:
    """Delete an item owned by the authenticated user.

    Args:
        id_param: UUID of the item to delete.
        service: Injected ItemService dependency.
        current_user: Must be the owner of the item.
        background_tasks: Background tasks manager.

    Returns:
        Confirmation message with HTTP 200 status code.

    """
    await service.delete_item(id_param, current_user)
    background_tasks.add_task(invalidate_items_namespace)
    return {"detail": "Item deleted successfully", "status_code": HTTP_204_NO_CONTENT}


@api_version(1)
@router.post("/image/{id_param}")
async def submit_an_item_image(  # noqa: PLR0913, PLR0917
    id_param: UUID,
    service: ItemServiceDep,
    image_file: ImageFile,
    background_tasks: BackgroundTasks,
    current_user: CurrentUserDep,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    """Upload an image to the configured media storage and attach it to an item.

    Args:
        id_param: UUID of the target item.
        service: Injected ItemService dependency.
        image_file: Image file to upload (multipart/form-data).
        background_tasks: Background tasks manager.
        current_user: Authenticated user who must own the item.
        caption: Optional alt-text or description for the image.

    Returns:
        The updated item with its new ``image_url``.

    """
    result = await service.update_item_image(
        id_param, image_file, caption, current_user
    )
    background_tasks.add_task(invalidate_items_namespace)
    return result


@api_version(1)
@router.post("/with-image/")
async def create_item_with_image(  # noqa: PLR0913, PLR0917
    service: ItemServiceDep,
    current_user: CurrentUserDep,
    background_tasks: BackgroundTasks,
    name: ItemName,
    description: ItemDescription = "No description provided",
    price: ItemPrice = 0.00,
    tax: ItemTax = 0.00,
    image_file: ImageFileOptional = None,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    """Create an item with an optional image in a single multipart request.

    Validates that no other item shares the same name before creation.
    If an image file is supplied it is uploaded and its URL stored on
    the newly created item.

    Args:
        service: Injected ItemService dependency.
        current_user: The authenticated user who will own the item.
        background_tasks: Background tasks manager.
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
    result = await service.create_item_with_image(
        name=name,
        description=description,
        price=price,
        tax=tax,
        owner=current_user,
        image_file=image_file,
        caption=caption,
    )
    background_tasks.add_task(invalidate_items_namespace)
    return result
