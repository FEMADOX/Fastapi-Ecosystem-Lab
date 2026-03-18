from typing import TYPE_CHECKING

from starlette.status import HTTP_403_FORBIDDEN

from learn_fastapi.src.utils.exceptions import build_http_exception

if TYPE_CHECKING:
    from fastapi import HTTPException


def only_user_owner_is_authorized() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_403_FORBIDDEN,
        detail="Only the user account owner is authorized to perform this action",
    )


def incorrect_password_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_403_FORBIDDEN,
        detail="Incorrect password",
    )
