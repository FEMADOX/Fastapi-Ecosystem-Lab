from hashlib import sha1
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import httpx
from fastapi import UploadFile

from learn_fastapi.src.config import settings
from learn_fastapi.src.constants import CLOUDINARY_ASSET_FOLDER
from learn_fastapi.src.utils.exceptions import image_filename_required_exception

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


def _sign_cloudinary_params(params: dict[str, str], api_secret: str) -> str:
    """Create a Cloudinary upload signature from signed request parameters.

    Args:
        params: The parameters to include in the signature, such as
            timestamp and public_id.
        api_secret: The Cloudinary API secret key.

    Returns:
        The SHA-1 hash signature string for the given parameters and API secret.

    """
    signature_payload = "&".join(
        f"{key}={value}" for key, value in sorted(params.items())
    )
    return sha1(f"{signature_payload}{api_secret}".encode()).hexdigest()  # noqa: S324


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

    """
    if not image_file.filename:
        raise image_filename_required_exception()

    cloud_name, api_key, api_secret = _get_cloudinary_config()
    timestamp = int(time())
    public_id = f"{uuid4()}-{timestamp}"
    upload_params = {
        "asset_folder": CLOUDINARY_ASSET_FOLDER,
        "public_id": public_id,
        "timestamp": str(timestamp),
    }
    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    image_bytes = await image_file.read()

    async with httpx.AsyncClient(timeout=CLOUDINARY_UPLOAD_TIMEOUT) as client:
        response = await client.post(
            upload_url,
            data={
                "api_key": api_key,
                "asset_folder": upload_params["asset_folder"],
                "public_id": upload_params["public_id"],
                "timestamp": upload_params["timestamp"],
                "signature": _sign_cloudinary_params(upload_params, api_secret),
            },
            files={
                "file": (
                    image_file.filename,
                    image_bytes,
                    image_file.content_type or "application/octet-stream",
                )
            },
        )
        response.raise_for_status()

    upload_result = response.json()
    return ImageSchema(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=upload_result["secure_url"],
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
    path_parts = parsed_url.path.split("/")

    return path_parts[-1].split(".")[0]


async def delete_image_file(image_public_id: str) -> bool:
    """Delete an image from Cloudinary.

    Args:
        image_public_id: The image ID to delete.

    Returns:
        Success: True | False

    """
    cloud_name, api_key, api_secret = _get_cloudinary_config()
    timestamp = int(time())
    delete_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/destroy"
    upload_params = {
        "public_id": image_public_id,
        "timestamp": str(timestamp),
    }

    async with httpx.AsyncClient(timeout=CLOUDINARY_UPLOAD_TIMEOUT) as client:
        response = await client.post(
            delete_url,
            data={
                "public_id": image_public_id,
                "api_key": api_key,
                "timestamp": upload_params["timestamp"],
                "signature": _sign_cloudinary_params(upload_params, api_secret),
            },
        )
        response.raise_for_status()

    # result = "ok" | "not found"
    return response.json()["result"] == "ok"
