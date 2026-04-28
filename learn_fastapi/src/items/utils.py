import aiofiles
from fastapi import UploadFile

from learn_fastapi.src.constants import IMAGES_DIR
from learn_fastapi.src.utils.exceptions import image_filename_required_exception

from .schema import ImageSchema


async def save_image_file(
    image_file: UploadFile, caption: str = "No description provided"
) -> ImageSchema:
    """Save the image to disk and return an ImageSchema.

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

    file_path = IMAGES_DIR / image_file.filename

    if not file_path.exists():
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await image_file.read())

    return ImageSchema(
        name=image_file.filename,
        description=caption,
        content_type=image_file.content_type,
        url=f"/media/images/{image_file.filename}",
    )
