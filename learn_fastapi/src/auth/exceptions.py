from fastapi import HTTPException
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
)

only_user_owner_is_authorized = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Only the user account owner is authorized to perform this action",
)
credentials_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
    headers={"WWW-Authenticate": "Bearer"},
)
email_already_registered_exception = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="Email already registered",
)
incorrect_password_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN,
    detail="Incorrect password",
)
invalid_expire_token_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
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
user_inactive_exception = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="Inactive user",
)
