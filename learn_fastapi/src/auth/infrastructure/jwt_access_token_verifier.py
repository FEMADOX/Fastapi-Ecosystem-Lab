import jwt

from learn_fastapi.src.auth.presentation.schemas import TokenData


def verify_access_token(token: str) -> TokenData | None:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
    except jwt.DecodeError:
        return None
    sub = payload.get("sub")
    exp = payload.get("exp")
    if not sub or exp is None:
        return None
    return TokenData(sub=sub, exp=exp)
