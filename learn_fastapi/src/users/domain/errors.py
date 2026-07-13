class UserDomainError(Exception):
    """Base class for all user domain errors."""


class IncorrectPasswordError(UserDomainError):
    """Raised when the password submitted is incorrect."""


class OnlyOwnerIsAuthorizedError(UserDomainError):
    """Raised when the action performed is only authorized by the owner."""


class UserDoesntExistError(UserDomainError):
    """Raised when the user requested doesn't exist."""


class UserInactiveError(UserDomainError):
    """Raised when the user account is inactive."""


class UserAlreadyExistsError(UserDomainError):
    """Raised when the user already exists."""
