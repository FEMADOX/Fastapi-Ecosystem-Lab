from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

only_user_owner_is_authorized = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="Only the user account owner is authorized to perform this action",
)
incorrect_password_exception = HTTPException(
    status_code=HTTP_403_FORBIDDEN,
    detail="Incorrect password",
)
