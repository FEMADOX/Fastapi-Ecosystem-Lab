from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_422_UNPROCESSABLE_CONTENT,
)


def build_http_exception(
    *,
    status_code: int,
    detail: str,
    headers: dict[str, str] | None = None,
) -> HTTPException:
    """Create a fresh FastAPI HTTPException instance.

    Using factories instead of module-level singleton exceptions keeps the
    error definitions consistent across modules and makes it easy to attach
    headers or richer JSON-able detail later without changing every caller.

    Args:
        status_code: The HTTP status code for the exception.
        detail: A human-readable message describing the error.
        headers: Optional HTTP headers to include in the response.

    Returns:
        A new HTTPException instance with
            the specified status code, detail, and headers.

    """
    return HTTPException(status_code=status_code, detail=detail, headers=headers)


def user_doesnt_exist_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="User does not exist",
    )


def user_inactive_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_400_BAD_REQUEST,
        detail="Inactive user",
    )


def email_already_registered_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )


def invalid_expire_token_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


def image_filename_required_exception() -> HTTPException:
    return build_http_exception(
        status_code=HTTP_422_UNPROCESSABLE_CONTENT,
        detail="Image file must have a filename",
    )
