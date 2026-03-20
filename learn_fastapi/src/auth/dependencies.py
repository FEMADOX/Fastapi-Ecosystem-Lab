from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from learn_fastapi.src.database import AsyncSessionDep

from .service import AuthService

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


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
