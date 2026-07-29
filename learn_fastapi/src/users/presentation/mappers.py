from learn_fastapi.src.users.domain.entities import PersistedUser
from learn_fastapi.src.users.presentation.schemas import UserResponse


def persisted_user_to_schema(persisted_user: PersistedUser) -> UserResponse:
    """Convert a Domain user to a schema user.

    Args:
        persisted_user: The domain user to convert.

    Returns:
        UserResponse: The corresponding schema user.

    """
    return UserResponse(
        id=persisted_user.id,
        email=persisted_user.email,
        is_active=persisted_user.is_active,
        is_superuser=persisted_user.is_superuser,
    )
