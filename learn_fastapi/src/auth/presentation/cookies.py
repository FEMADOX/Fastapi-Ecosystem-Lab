from starlette.responses import Response

from learn_fastapi.src.auth.config import auth_config

AUTH_COOKIE_PATH = "/"


def set_auth_cookies(response: Response, refresh_token: str, csrf_token: str) -> None:
    max_age = int(auth_config.refresh_token_expire.total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=auth_config.cookie_secure,
        samesite=auth_config.cookie_samesite,
        max_age=max_age,
        path=AUTH_COOKIE_PATH,
        domain=auth_config.cookie_domain,
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        secure=auth_config.cookie_secure,
        samesite=auth_config.cookie_samesite,
        max_age=max_age,
        path=AUTH_COOKIE_PATH,
        domain=auth_config.cookie_domain,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token", path=AUTH_COOKIE_PATH, domain=auth_config.cookie_domain
    )
    response.delete_cookie(
        key="csrf_token", path=AUTH_COOKIE_PATH, domain=auth_config.cookie_domain
    )
