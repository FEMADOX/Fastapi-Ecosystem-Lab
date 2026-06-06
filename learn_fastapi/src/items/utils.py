from hashlib import sha1
from time import time
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


def _sign_cloudinary_params(params: dict[str, int | str], api_secret: str) -> str:
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
        "timestamp": timestamp,
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
                "timestamp": str(upload_params["timestamp"]),
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
