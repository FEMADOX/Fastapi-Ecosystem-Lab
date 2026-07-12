from asyncio import to_thread
from pathlib import PurePosixPath
from re import fullmatch
from time import time
from typing import Any
from urllib.parse import urlparse
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from learn_fastapi.src.config import settings
from learn_fastapi.src.constants import CLOUDINARY_ASSET_FOLDER
from learn_fastapi.src.shared.presentation.exceptions import (
    image_filename_required_exception,
)

from .schema import ImageSchema

CLOUDINARY_UPLOAD_TIMEOUT = 60


def _get_cloudinary_config() -> tuple[str, str, str]:
    """Return Cloudinary credentials or raise when image uploads are unavailable.

    Returns:
        A tuple of (cloud_name, api_key, api_secret) for Cloudinary uploads.

    Raises:
        RuntimeError:
            If any of the required Cloudinary environment variables are missing.

    """
    if (
        not settings.cloudinary_cloud_name
        or not settings.cloudinary_api_key
        or not settings.cloudinary_api_secret
    ):
        msg = "Cloudinary environment variables are not configured."
        raise RuntimeError(msg)

    return (
        settings.cloudinary_cloud_name,
        settings.cloudinary_api_key.get_secret_value(),
        settings.cloudinary_api_secret.get_secret_value(),
    )


def _configure_cloudinary() -> None:
    """Configure Cloudinary's SDK from application settings."""
    cloud_name, api_key, api_secret = _get_cloudinary_config()
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


async def save_image_file(
    image_file: UploadFile, caption: str = "No description provided"
) -> ImageSchema:
    """Upload the image to Cloudinary and return an ImageSchema.

    Args:
        image_file: The uploaded image file.
        caption: A description for the image.

    Returns:
        ImageSchema with the saved file metadata.

    Raises:
        image_filename_required_exception: If the image file does not have a filename.
        TypeError:
            If the Cloudinary upload response does not include a valid secure_url
            or public_id.

    """
    if not image_file.filename:
        raise image_filename_required_exception()

    _configure_cloudinary()
    timestamp = int(time())
    public_id = f"{uuid4()}-{timestamp}"

    await image_file.seek(0)
    # The Cloudinary SDK signs and sends the request for us; running it in a
    #   thread keeps the async endpoint from blocking on network I/O.
    upload_result: dict[str, Any] = await to_thread(
        cloudinary.uploader.upload,
        image_file.file,
        asset_folder=CLOUDINARY_ASSET_FOLDER,
        public_id=public_id,
        resource_type="image",
        timeout=CLOUDINARY_UPLOAD_TIMEOUT,
    )
    image_url = upload_result.get("secure_url")
    if not isinstance(image_url, str):
        msg = "Cloudinary upload response did not include secure_url."
        raise TypeError(msg)

    image_public_id = upload_result.get("public_id")
    if not isinstance(image_public_id, str):
        msg = "Cloudinary upload response did not include public_id."
        raise TypeError(msg)

    return ImageSchema(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=upload_result["secure_url"],
        public_id=image_public_id,
    )


def extract_cloudinary_public_id(image_url: str) -> str:
    """Extract the Cloudinary public ID from the image URL.

    Args:
        image_url: The full URL of the uploaded image.

    Returns:
        The public ID string used by Cloudinary to identify the image.

    """
    # Cloudinary URLs are typically in the format:
    # https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
    # We can use urlparse to extract the path and then split it to get the public_id
    parsed_url = urlparse(image_url)
    path_parts = [part for part in parsed_url.path.split("/") if part]
    if not path_parts:
        return ""

    if "upload" not in path_parts:
        return PurePosixPath(path_parts[-1]).with_suffix("").as_posix()

    public_id_parts = path_parts[path_parts.index("upload") + 1 :]
    for index, part in enumerate(public_id_parts):
        if fullmatch(r"v\d+", part):
            public_id_parts = public_id_parts[index + 1 :]
            break

    if not public_id_parts:
        return ""

    return PurePosixPath("/".join(public_id_parts)).with_suffix("").as_posix()


async def delete_image_file(image_public_id: str) -> bool:
    """Delete an image from Cloudinary.

    Args:
        image_public_id: The image ID to delete.

    Returns:
        Success: True | False

    """
    if not image_public_id:
        return False

    _configure_cloudinary()
    delete_result: dict[str, Any] = await to_thread(
        cloudinary.uploader.destroy,
        image_public_id,
        resource_type="image",
        invalidate=True,
    )

    # result = "ok" | "not found"
    return delete_result.get("result") == "ok"
