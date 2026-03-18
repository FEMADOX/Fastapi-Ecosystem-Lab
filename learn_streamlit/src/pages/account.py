"""Account page: view profile, update email/password, delete account."""

import streamlit as st

from learn_streamlit.src.api_client import delete_account, get_me, update_account
from learn_streamlit.src.pages.auth import is_authenticated


def _load_profile() -> dict | None:
    if not is_authenticated():
        st.warning("Please log in to view your account.")
        return None
    result = get_me()
    if isinstance(result, str):
        st.error(result)
        return None
    return result


def show_profile(user: dict) -> None:
    st.subheader("Profile")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**User ID:** `{user['id']}`")
    st.write(f"**Superuser:** {'Yes' if user.get('is_superuser') else 'No'}")


def show_update(user: dict) -> None:
    st.subheader("Update Account")
    with st.form("update_account_form"):
        current_password = st.text_input("Current Password (required)", type="password")
        new_email = st.text_input("New Email (leave blank to keep)")
        new_password = st.text_input(
            "New Password (leave blank to keep)", type="password"
        )
        submitted = st.form_submit_button("Update")

    if submitted:
        if not current_password:
            st.warning("Current password is required.")
            return
        if not new_email and not new_password:
            st.warning("Provide a new email or password to update.")
            return
        result = update_account(
            user["id"],
            current_password,
            new_email or None,
            new_password or None,
        )
        if isinstance(result, dict):
            st.success("Account updated!")
        else:
            st.error(result)


def show_delete(user: dict) -> None:
    st.subheader("Delete Account")
    st.warning("This action is **irreversible**.")
    with st.form("delete_account_form"):
        password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Delete My Account")

    if submitted:
        if not password:
            st.warning("Please enter your password.")
            return
        result = delete_account(user["id"], password)
        if result is True:
            st.success("Account deleted.")
            st.rerun()
        else:
            st.error(result)


def render() -> None:
    user = _load_profile()
    if not user:
        return

    tab_profile, tab_update, tab_delete = st.tabs(["Profile", "Update", "Delete"])
    with tab_profile:
        show_profile(user)
    with tab_update:
        show_update(user)
    with tab_delete:
        show_delete(user)
