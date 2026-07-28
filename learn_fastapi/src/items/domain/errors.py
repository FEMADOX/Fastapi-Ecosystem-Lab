class ItemDomainError(Exception):
    """Base class for all item domain errors."""


class ItemNotFoundError(ItemDomainError):
    """Raised when an item is not found in the repository."""


class ItemDuplicatedNameError(ItemDomainError):
    """Raised when an item with the same name already exists in the repository."""


class ItemNotBelongToUserError(ItemDomainError):
    """Raised when an item does not belong to the user."""


class ItemNotFoundForUserError(ItemDomainError):
    """Raised when no item is found for the user."""


class ItemsNotFoundForUserError(ItemDomainError):
    """Raised when no items are found for the user."""


class ItemsForbiddenOwnerAccessError(ItemDomainError):
    """Raised when an item does not belong to the user."""
