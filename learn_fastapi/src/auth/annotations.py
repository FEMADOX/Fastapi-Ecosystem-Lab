from typing import Annotated

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import mapped_column

# ---------------------------------------------------------------------------
# SQLAlchemy ORM column type annotations
# ---------------------------------------------------------------------------

str_idx_unique = Annotated[str, mapped_column(unique=True, index=True)]
bool_default_true = Annotated[bool, mapped_column(default=True)]
bool_default_false = Annotated[bool, mapped_column(default=False)]

# ---------------------------------------------------------------------------
# OAuth2 annotations
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

OAuth2_Dep = Annotated[str, Depends(oauth2_scheme)]
