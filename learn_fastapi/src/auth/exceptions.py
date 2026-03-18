from typing import TYPE_CHECKING

from starlette.status import HTTP_401_UNAUTHORIZED

from learn_fastapi.src.utils.exceptions import build_http_exception

if TYPE_CHECKING:
    from fastapi import HTTPException


def credentials_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def invalid_refresh_or_csrf_token_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token or CSRF token",
    )


def invalid_refresh_token_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
