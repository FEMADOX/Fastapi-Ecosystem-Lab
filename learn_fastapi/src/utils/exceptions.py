from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

user_doesnt_exist_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="User does not exist",
)
user_inactive_exception = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="Inactive user",
)
email_already_registered_exception = HTTPException(
    status_code=HTTP_400_BAD_REQUEST,
    detail="Email already registered",
)
invalid_expire_token_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)
