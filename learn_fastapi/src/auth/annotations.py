from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import mapped_column

# OAuth2 scheme definition
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------

str_idx_unique = Annotated[str, mapped_column(unique=True, index=True)]
bool_default_true = Annotated[bool, mapped_column(default=True)]
bool_default_false = Annotated[bool, mapped_column(default=False)]

# ---------------------------------------------------------------------------
# Auth annotations
# ---------------------------------------------------------------------------

OAuth2PRFDep = Annotated[OAuth2PasswordRequestForm, Depends()]
OAuth2_Dep = Annotated[str, Depends(oauth2_scheme)]
