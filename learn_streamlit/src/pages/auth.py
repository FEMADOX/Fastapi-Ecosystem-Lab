"""Authentication pages: Login and Register."""

import streamlit as st

from learn_streamlit.src.api_client import login, register


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def show_login() -> None:
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not email or not password:
            st.warning("Please fill in both fields.")
            return
        result = login(email, password)
        if isinstance(result, dict):
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(result)


def show_register() -> None:
    st.subheader("Register")
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Register")

    if submitted:
        if not email or not password:
            st.warning("Please fill in all fields.")
            return
        if password != confirm:
            st.warning("Passwords do not match.")
            return
        if len(password) < 8:
            st.warning("Password must be at least 8 characters.")
            return
        result = register(email, password)
        if isinstance(result, dict):
            st.success(f"Account created for **{result['email']}**. You can now login.")
        else:
            st.error(result)


def render() -> None:
    tab_login, tab_register = st.tabs(["Login", "Register"])
    with tab_login:
        show_login()
    with tab_register:
        show_register()
