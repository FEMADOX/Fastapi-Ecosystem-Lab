class AuthDomainError(Exception):
    """Base class for all auth domain errors."""


class CredentialsError(AuthDomainError):
    """Raised when an incorrect email or password has been submited."""


class InvalidRefreshOrCsrfTokenError(AuthDomainError):
    """Raised when an invalid refresh token or CSRF token has been submited."""


class InvalidRefreshTokenError(AuthDomainError):
    """Raised when an invalid or expired refresh token has been submited."""


class DoesntExistUserError(AuthDomainError):
    """Raised when the user requested doesn't exist."""


class DoesntExistRefreshTokenError(AuthDomainError):
    """Raised when the refresh token requested doesn't exist."""
