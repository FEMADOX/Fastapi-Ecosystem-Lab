# TODO (FEMADOX): This file is not longer necessary, but it is left here for demonstration purposes.
#   It shows how to define a validator function that can be applied to a Pydantic model.
#   In this case, we define a `validate_item` function that checks the length of the `name` and `description` fields, as well as the values of the `price` and `tax` fields.
#   If any of these checks fail, a `ValueError` is raised with an appropriate message. If all checks pass, the original `Item` instance is returned.

from .schema import Item


def validate_item(item: Item) -> Item:
    if len(item.name) < 3:
        msg = "Name must be at least 3 characters long"
        raise ValueError(msg)
    if len(item.description) < 20:
        msg = "Description must be at least 20 characters long"
        raise ValueError(msg)
    if item.price < 0:
        msg = "Price must be greater than or equal to 0"
        raise ValueError(msg)
    if item.tax < 0:
        msg = "Tax must be greater than or equal to 0"
        raise ValueError(msg)
    return item
