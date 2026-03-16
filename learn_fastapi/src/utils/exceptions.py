from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

user_doesnt_exist_exception = HTTPException(
    status_code=HTTP_401_UNAUTHORIZED,
    detail="User does not exist",
)
