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
