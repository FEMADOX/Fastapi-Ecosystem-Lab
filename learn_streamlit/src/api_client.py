"""HTTP client wrapper for the learn_fastapi backend API."""

import httpx
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"


def _auth_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _extract_error(response: httpx.Response) -> str:
    """Normalize FastAPI error responses into a single string."""
    try:
        body = response.json()
    except Exception:
        return response.text

    detail = body.get("detail", "")
    if isinstance(detail, list):
        return "; ".join(
            f"{'.'.join(str(loc) for loc in exceptions.get('loc', []))}: {
                exceptions.get('msg', '')
            }"
            for exceptions in detail
        )
    return str(detail) if detail else response.text


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def register(email: str, password: str) -> dict | str:
    response = httpx.post(
        f"{API_BASE}/auth/register", json={"email": email, "password": password}
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def login(email: str, password: str) -> dict | str:
    response = httpx.post(
        f"{API_BASE}/auth/token",
        data={"username": email, "password": password},
    )

    if not response.is_success:
        return _extract_error(response)

    data = response.json()
    st.session_state["access_token"] = data["access_token"]
    st.session_state["csrf_token"] = data.get("csrf_token", "")
    st.session_state["expires_in"] = data.get("expires_in", 0)

    for cookie in response.cookies.jar:
        if cookie.name == "refresh_token":
            st.session_state["refresh_token"] = cookie.value
        if cookie.name == "csrf_token":
            st.session_state["csrf_cookie"] = cookie.value

    user_data = get_me()
    if isinstance(user_data, dict):
        st.session_state["user_id"] = user_data["id"]
        st.session_state["is_admin"] = user_data["is_admin"]

    return data


def logout() -> None:
    headers = _auth_headers()
    csrf = st.session_state.get("csrf_token", "")
    if csrf:
        headers["X-CSRF-Token"] = csrf

    cookies = {}
    if "refresh_token" in st.session_state:
        cookies["refresh_token"] = st.session_state["refresh_token"]
    if "csrf_cookie" in st.session_state:
        cookies["csrf_token"] = st.session_state["csrf_cookie"]

    httpx.post(f"{API_BASE}/auth/logout", headers=headers, cookies=cookies)

    for key in (
        "access_token",
        "csrf_token",
        "refresh_token",
        "csrf_cookie",
        "expires_in",
        "user",
        "user_id",
    ):
        st.session_state.pop(key, None)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


def get_me() -> dict | str:
    response = httpx.get(f"{API_BASE}/users/me", headers=_auth_headers())

    if not response.is_success:
        return _extract_error(response)

    return response.json()


def update_account(
    user_id: str, current_password: str, new_email: str | None, new_password: str | None
) -> dict | str:
    payload: dict = {"current_password": current_password}
    if new_email:
        payload["new_email"] = new_email
    if new_password:
        payload["new_password"] = new_password
    response = httpx.patch(
        f"{API_BASE}/users/{user_id}", json=payload, headers=_auth_headers()
    )

    if not response.is_success:
        return _extract_error(response)

    return response.json()


def delete_account(user_id: str, password: str) -> bool | str:
    response = httpx.request(
        "DELETE",
        f"{API_BASE}/users/{user_id}",
        json={"password": password},
        headers=_auth_headers(),
    )

    if not response.is_success:
        return _extract_error(response)

    logout()
    return True


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------


def get_items() -> list[dict]:
    response = httpx.get(f"{API_BASE}/items/")

    if not response.is_success:
        return []

    return response.json()


def get_item(item_id: str) -> dict | str:
    response = httpx.get(f"{API_BASE}/items/{item_id}")

    if response.is_success:
        return _extract_error(response)

    return response.json()


def create_item(name: str, description: str, price: float, tax: float) -> dict | str:
    response = httpx.post(
        f"{API_BASE}/items/",
        json={"name": name, "description": description, "price": price, "tax": tax},
        headers=_auth_headers(),
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def update_item(
    item_id: str, name: str, description: str, price: float, tax: float
) -> dict | str:
    response = httpx.put(
        f"{API_BASE}/items/{item_id}",
        json={"name": name, "description": description, "price": price, "tax": tax},
        headers=_auth_headers(),
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def patch_item(item_id: str, **fields: object) -> dict | str:
    response = httpx.patch(
        f"{API_BASE}/items/{item_id}",
        json=fields,
        headers=_auth_headers(),
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def delete_item(item_id: str) -> dict | str:
    response = httpx.delete(f"{API_BASE}/items/{item_id}", headers=_auth_headers())
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def upload_item_image(
    item_id: str,
    file_bytes: bytes,
    filename: str,
    caption: str = "No description provided",
) -> dict | str:
    response = httpx.post(
        f"{API_BASE}/items/image/{item_id}",
        files={"image_file": (filename, file_bytes)},
        data={"caption": caption},
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def create_item_with_image(  # noqa: PLR0913, PLR0917
    name: str,
    description: str,
    price: float,
    tax: float,
    file_bytes: bytes | None = None,
    filename: str | None = None,
    caption: str = "No description provided",
) -> dict | str:
    data_fields = {
        "name": name,
        "description": description,
        "price": str(price),
        "tax": str(tax),
        "caption": caption,
    }
    files = {}
    if file_bytes and filename:
        files["image_file"] = (filename, file_bytes)
    response = httpx.post(
        f"{API_BASE}/items/with-image/",
        data=data_fields,
        files=files or None,
        headers=_auth_headers(),
    )
    if not response.is_success:
        return _extract_error(response)
    return response.json()


def get_image_url(filename: str) -> str:
    return f"{API_BASE}/items/image/?filename={filename}"
