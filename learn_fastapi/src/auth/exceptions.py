from fastapi import HTTPException
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
)

credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)
invalid_refresh_or_csrf_token_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid refresh token or CSRF token",
)
invalid_refresh_token_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired refresh token",
)
