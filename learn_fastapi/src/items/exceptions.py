from typing import TYPE_CHECKING

from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from learn_fastapi.src.utils.exceptions import build_http_exception

if TYPE_CHECKING:
    from fastapi import HTTPException


def image_not_found_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_404_NOT_FOUND,
        detail="Image not found",
    )


def item_not_found_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_404_NOT_FOUND,
        detail="Item not found",
    )


def item_not_found_or_not_belong_to_user_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_404_NOT_FOUND,
        detail="Item not found or does not belong to the user",
    )


def items_not_found_for_user_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_404_NOT_FOUND,
        detail="No items found for the user",
    )


def duplicate_item_name_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_409_CONFLICT,
        detail="An item with this name already exists",
    )
