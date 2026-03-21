"""Streamlit frontend for the Learn FastAPI backend."""

import importlib

import streamlit as st

from learn_streamlit.src.api_client import logout
from learn_streamlit.src import account, auth, items
from learn_streamlit.src.account import render as account_render
from learn_streamlit.src.auth import is_authenticated
from learn_streamlit.src.auth import render as auth_render
from learn_streamlit.src.items import render as items_render


def _load_pages_modules() -> tuple[object, object, object]:
    """Reload local page modules so edits are reflected during development."""
    auth_module = importlib.reload(auth)
    account_module = importlib.reload(account)
    items_module = importlib.reload(items)
    return auth_module, account_module, items_module


def render() -> None:
    auth_module, account_module, items_module = _load_pages_modules()

    st.set_page_config(page_title="Learn FastAPI", page_icon="⚡", layout="wide")

    # Sidebar navigation
    st.sidebar.title("Learn FastAPI")

    pages: dict[str, str] = {
        "Items": "items",
        "Auth": "auth",
        "Account": "account",
    }

    page_options = list(pages.keys()) if is_authenticated() else ["Items", "Auth"]
    selection = st.sidebar.radio("Navigate", page_options, label_visibility="collapsed")

    if is_authenticated():
        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            logout()
            st.rerun()

    page_key = pages.get(selection, "items")

    if page_key == "items":
        items_render()
    elif page_key == "auth":
        if is_authenticated():
            st.info("You are already logged in.")
        else:
            auth_render()
    elif page_key == "account":
        account_render()


render()
