from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

item_not_found_exception = HTTPException(
    status_code=HTTP_404_NOT_FOUND, detail="Item not found"
)
item_not_found_or_not_belong_to_user_exception = HTTPException(
    status_code=HTTP_404_NOT_FOUND,
    detail="Item not found or does not belong to the user",
)
items_not_found_for_user_exception = HTTPException(
    status_code=HTTP_404_NOT_FOUND,
    detail="No items found for the user",
)
