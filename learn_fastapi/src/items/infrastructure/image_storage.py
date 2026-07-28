from asyncio import to_thread
from time import time
from typing import Any
from uuid import uuid4

import cloudinary
import cloudinary.uploader

from learn_fastapi.src.config import settings
from learn_fastapi.src.constants import CLOUDINARY_ASSET_FOLDER
from learn_fastapi.src.items.application.errors import InvalidImageUploadError
from learn_fastapi.src.items.application.ports import ImageUpload
from learn_fastapi.src.items.domain.entities import (
    ItemImage,
)
from learn_fastapi.src.items.domain.value_objects import ImagePublicId

CLOUDINARY_UPLOAD_TIMEOUT: int = 60


class CloudinaryImageStorage:
    """Cloudinary Adapter."""

    @staticmethod
    def _configure() -> None:
        """Set the configuration for the cloudinary.

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

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key.get_secret_value(),
            api_secret=settings.cloudinary_api_secret.get_secret_value(),
            secure=True,
        )

    async def upload(
        self,
        image_file: ImageUpload,
        caption: str | None,
    ) -> ItemImage:
        """Upload the image to Cloudinary and return an ImageSchema.

        Args:
            image_file: The uploaded image file.
            caption: A description for the image.

        Returns:
            ItemImage domain entities with the saved file metadata.

        Raises:
            InvalidImageUploadError:
                If the image file does not have a filename.
            TypeError:
                If the Cloudinary upload response does not include a valid secure_url
                or public_id.

        """
        if not image_file.filename:
            raise InvalidImageUploadError

        self._configure()
        timestamp = int(time())
        public_id = f"{uuid4()}-{timestamp}"

        await image_file.seek(0)

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

        return ItemImage(
            name=image_file.filename,
            description=caption,
            content_type=image_file.content_type,
            url=upload_result["secure_url"],
            public_id=image_public_id,
        )

    async def delete(self, image_public_id: ImagePublicId) -> bool:
        """Delete an image from Cloudinary.

        Args:
            image_public_id: The image ID to delete.

        Returns:
            Success: True | False

        """
        self._configure()

        delete_result: dict[str, Any] = await to_thread(
            cloudinary.uploader.destroy,
            image_public_id,
            resource_type="image",
            invalidate=True,
        )

        return delete_result.get("result") == "ok"
