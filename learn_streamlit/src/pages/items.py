"""Items pages: browse, create, edit, delete, and image management."""

import streamlit as st

from learn_streamlit.src.api_client import (
    API_BASE,
    create_item,
    create_item_with_image,
    delete_item,
    get_items,
    update_item,
    upload_item_image,
)
from learn_streamlit.src.pages.auth import is_authenticated


def _show_item_card(item: dict) -> None:
    """Render a single item card inside a container."""
    with st.container(border=True):
        col_info, col_img = st.columns([3, 1])
        with col_info:
            st.markdown(f"**{item['name']}**")
            st.caption(item.get("description", ""))
            price = item.get("price", 0)
            tax = item.get("tax", 0)
            st.write(f"Price: ${price:.2f}")
            st.write(f"Tax: ${tax:.2f}")
            st.write(f"Total: ${price + tax:.2f}")
        with col_img:
            image_url = item.get("image_url")
            if image_url:
                st.image(f"{API_BASE}{image_url}", width=100)


def display_items(items: list[dict[str, str]]) -> None:
    current_user_id = str(st.session_state.get("user_id"))
    is_admin = str(st.session_state.get("is_admin"))

    for item in items:
        _show_item_card(item)

        is_owner = bool(
            current_user_id and (str(item.get("user_id", "")) == current_user_id)
        )
        if not is_owner or not is_admin:
            continue

        butt_edit, butt_del, butt_img = st.columns(3)
        with butt_edit:
            if st.button("Edit", key=f"edit_{item['id']}"):
                st.session_state["editing_item"] = item
                st.rerun()
        with butt_del:
            if st.button("Delete", key=f"del_{item['id']}"):
                result = delete_item(item["id"])
                if isinstance(result, dict):
                    st.success(result.get("detail", "Deleted"))
                    st.rerun()
                else:
                    st.error(result)
        with butt_img:
            if st.button("Upload Image", key=f"img_{item['id']}"):
                st.session_state["uploading_image_for"] = item["id"]
                st.rerun()


def show_item_list() -> None:
    st.subheader("All Items")

    if st.button("Refresh", key="refresh_items"):
        st.rerun()

    items = get_items()
    if not items:
        st.info("No items yet.")
        return

    display_items(items)


def show_create_item() -> None:
    st.subheader("Create Item")
    use_image = st.checkbox("Include image")

    with st.form("create_item_form"):
        name = st.text_input("Name (min 3 chars)")
        description = st.text_area(
            "Description (min 10 chars)", value="No description provided"
        )
        price = st.number_input("Price", min_value=0.0, value=0.0, step=0.01)
        tax = st.number_input("Tax", min_value=0.0, value=0.0, step=0.01)

        file_bytes = None
        filename = None
        caption = "No description provided"
        if use_image:
            uploaded = st.file_uploader("Image", type=["png", "jpg", "jpeg", "webp"])
            caption = st.text_input("Caption", value="No description provided")
            if uploaded:
                file_bytes = uploaded.getvalue()
                filename = uploaded.name

        submitted = st.form_submit_button("Create")

    if submitted:
        if len(name) < 3:
            st.warning("Name must be at least 3 characters.")
            return

        if use_image:
            result = create_item_with_image(
                name, description, price, tax, file_bytes, filename, caption
            )
        else:
            result = create_item(name, description, price, tax)

        if isinstance(result, dict):
            st.success(f"Item **{result['name']}** created!")
        else:
            st.error(result)


def show_edit_item() -> None:
    item = st.session_state.get("editing_item")
    if not item:
        return

    st.subheader(f"Editing: {item['name']}")

    if st.button("Cancel editing"):
        st.session_state.pop("editing_item", None)
        st.rerun()

    with st.form("edit_item_form"):
        name = st.text_input("Name", value=item["name"])
        description = st.text_area("Description", value=item.get("description", ""))
        price = st.number_input(
            "Price", min_value=0.0, value=float(item.get("price", 0)), step=0.01
        )
        tax = st.number_input(
            "Tax", min_value=0.0, value=float(item.get("tax", 0)), step=0.01
        )
        submitted = st.form_submit_button("Save")

    if submitted:
        result = update_item(item["id"], name, description, price, tax)
        if isinstance(result, dict):
            st.success("Item updated!")
            st.session_state.pop("editing_item", None)
            st.rerun()
        else:
            st.error(result)


def show_upload_image() -> None:
    item_id = st.session_state.get("uploading_image_for")
    if not item_id:
        return

    st.subheader("Upload Image")

    if st.button("Cancel upload"):
        st.session_state.pop("uploading_image_for", None)
        st.rerun()

    with st.form("upload_image_form"):
        uploaded = st.file_uploader("Choose image", type=["png", "jpg", "jpeg", "webp"])
        caption = st.text_input("Caption", value="No description provided")
        submitted = st.form_submit_button("Upload")

    if submitted:
        if not uploaded:
            st.warning("Please select a file.")
            return
        result = upload_item_image(item_id, uploaded.getvalue(), uploaded.name, caption)
        if isinstance(result, dict):
            st.success("Image uploaded!")
            st.session_state.pop("uploading_image_for", None)
            st.rerun()
        else:
            st.error(result)


def render() -> None:
    if st.session_state.get("editing_item"):
        show_edit_item()
        return

    if st.session_state.get("uploading_image_for"):
        show_upload_image()
        return

    tab_browse, tab_create = st.tabs(["Browse Items", "Create Item"])
    with tab_browse:
        show_item_list()
    with tab_create:
        if is_authenticated():
            show_create_item()
        else:
            st.info("Login to create items.")
