from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from learn_fastapi.src.database import AsyncSessionDep

from .service import AuthService, AuthServiceV2

OAuth2PRFDep = Annotated[OAuth2PasswordRequestForm, Depends()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")
OAuth2_Dep = Annotated[str, Depends(oauth2_scheme)]


def get_auth_service(session: AsyncSessionDep) -> AuthService:
    """Build an ``AuthService`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``AuthService`` instance.

    """
    return AuthService(session)


def get_auth_service_v2(session: AsyncSessionDep) -> AuthServiceV2:
    """Build an ``AuthServiceV2`` for the current request.

    Args:
        session: The database session dependency for the request.

    Returns:
        A configured ``AuthServiceV2`` instance.

    """
    return AuthServiceV2(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
AuthServiceV2Dep = Annotated[AuthServiceV2, Depends(get_auth_service_v2)]
