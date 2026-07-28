from uuid import UUID

from fastapi import APIRouter
from fastapi_versionizer.versionizer import api_version
from starlette.status import HTTP_204_NO_CONTENT

from learn_fastapi.src.items.annotations import (
    AnnotatedOwnerId,
    ImageCaption,
    ImageFile,
    ItemDescription,
    ItemName,
    ItemPrice,
    ItemTax,
)
from learn_fastapi.src.items.application.commands import (
    CreateItemCommand,
    CreateItemWithImageCommand,
    DeleteItemCommand,
    PatchItemCommand,
    UpdateItemCommand,
    UpdateItemImageCommand,
)
from learn_fastapi.src.items.application.errors import InvalidImageUploadError
from learn_fastapi.src.items.application.queries import (
    GetItemQuery,
    GetOwnerItemQuery,
    ListOwnerItemsQuery,
)
from learn_fastapi.src.items.domain.errors import (
    ItemDuplicatedNameError,
    ItemNotFoundError,
    ItemNotFoundForUserError,
    ItemsForbiddenOwnerAccessError,
    ItemsNotFoundForUserError,
)
from learn_fastapi.src.items.presentation.dependencies import ItemsUseCasesDep
from learn_fastapi.src.items.presentation.exceptions import (
    duplicate_item_name_exception,
    item_not_found_exception,
    item_not_found_or_not_belong_to_user_exception,
)
from learn_fastapi.src.items.presentation.mappers import (
    current_actor_from_user,
    item_from_update_schema,
    persisted_item_to_schema,
    persisted_item_with_image_to_schema,
    persisted_items_to_schema,
)
from learn_fastapi.src.items.presentation.schemas import (
    ItemPatchSchema,
    ItemSchema,
    ItemUpdateSchema,
)
from learn_fastapi.src.shared.presentation.dependencies import CurrentUserDep
from learn_fastapi.src.shared.presentation.exceptions import (
    image_filename_required_exception,
)
from learn_fastapi.src.users.presentation.exceptions import (
    only_user_owner_is_authorized,
)

router = APIRouter(prefix="/items", tags=["items"])


@api_version(1)
@router.get("/")
async def read_items(use_cases: ItemsUseCasesDep) -> list[ItemSchema]:
    items = await use_cases.list_items.execute()
    return persisted_items_to_schema(items)


@api_version(1)
@router.get("/owner")
async def read_owner_items(
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
    owner_id: AnnotatedOwnerId = None,
) -> list[ItemSchema]:
    try:
        items = await use_cases.list_owner_items.execute(
            ListOwnerItemsQuery(current_actor_from_user(current_user), owner_id)
        )
    except ItemsForbiddenOwnerAccessError as exc:
        raise only_user_owner_is_authorized() from exc
    except ItemsNotFoundForUserError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc

    return persisted_items_to_schema(items)


@api_version(1)
@router.get("/owner/{id_param}")
async def read_owner_item(
    id_param: UUID,
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
    owner_id: AnnotatedOwnerId = None,
) -> ItemSchema:
    try:
        item = await use_cases.get_owner_item.execute(
            GetOwnerItemQuery(
                id_param,
                current_actor_from_user(current_user),
                owner_id,
            )
        )
    except ItemsForbiddenOwnerAccessError as exc:
        raise only_user_owner_is_authorized() from exc
    except ItemNotFoundForUserError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc

    return persisted_item_to_schema(item)


@api_version(1)
@router.get("/{id_param}")
async def read_item(id_param: UUID, use_cases: ItemsUseCasesDep) -> ItemSchema:
    try:
        item = await use_cases.get_item.execute(GetItemQuery(id_param))
    except ItemNotFoundError as exc:
        raise item_not_found_exception() from exc

    return persisted_item_to_schema(item)


@api_version(1)
@router.post("/")
async def create_item(
    item: ItemUpdateSchema,
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
) -> ItemSchema:
    domain_item = item_from_update_schema(item, current_user.id)
    created = await use_cases.create_item.execute(
        CreateItemCommand(domain_item, current_user.id)
    )
    return persisted_item_to_schema(created)


@api_version(1)
@router.put("/{id_param}")
async def update_item(
    id_param: UUID,
    item_param: ItemUpdateSchema,
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
) -> ItemSchema:
    domain_item = item_from_update_schema(item_param, current_user.id)
    try:
        updated = await use_cases.update_item.execute(
            UpdateItemCommand(
                id_param, current_user.id, current_user.is_superuser, domain_item
            )
        )
    except ItemNotFoundError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc

    return persisted_item_to_schema(updated)


@api_version(1)
@router.patch("/{id_param}")
async def patch_item(
    id_param: UUID,
    item_param: ItemPatchSchema,
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
) -> ItemSchema:
    fields = item_param.model_dump(exclude_unset=True, exclude_none=True)
    try:
        patched = await use_cases.patch_item.execute(
            PatchItemCommand(
                id_param, current_user.id, current_user.is_superuser, fields
            )
        )
    except ItemNotFoundError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc

    return persisted_item_to_schema(patched)


@api_version(1)
@router.delete("/{id_param}")
async def delete_item(
    id_param: UUID,
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
) -> dict[str, str | int]:
    try:
        await use_cases.delete_item.execute(
            DeleteItemCommand(id_param, current_user.id, current_user.is_superuser)
        )
    except ItemNotFoundError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc

    return {"detail": "Item deleted successfully", "status_code": HTTP_204_NO_CONTENT}


@api_version(1)
@router.post("/image/{id_param}")
async def submit_an_item_image(  # noqa: PLR0913, PLR0917
    id_param: UUID,
    use_cases: ItemsUseCasesDep,
    image_file: ImageFile,
    current_user: CurrentUserDep,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    try:
        item = await use_cases.update_item_image.execute(
            UpdateItemImageCommand(
                id_param,
                current_user.id,
                current_user.is_superuser,
                image_file,
                caption,
            )
        )
    except ItemNotFoundError as exc:
        raise item_not_found_or_not_belong_to_user_exception() from exc
    except InvalidImageUploadError as exc:
        raise image_filename_required_exception() from exc

    return persisted_item_with_image_to_schema(item)


@api_version(1)
@router.post("/with-image/")
async def create_item_with_image(  # noqa: PLR0913, PLR0917
    use_cases: ItemsUseCasesDep,
    current_user: CurrentUserDep,
    name: ItemName,
    image_file: ImageFile,
    description: ItemDescription = "No description provided",
    price: ItemPrice = 0.00,
    tax: ItemTax = 0.00,
    caption: ImageCaption = "No description provided",
) -> ItemSchema:
    try:
        new_item = await use_cases.create_item_with_image.execute(
            CreateItemWithImageCommand(
                current_user.id, name, price, tax, image_file, caption, description
            )
        )
    except ItemDuplicatedNameError as exc:
        raise duplicate_item_name_exception() from exc
    except InvalidImageUploadError as exc:
        raise image_filename_required_exception() from exc

    return persisted_item_with_image_to_schema(new_item)
