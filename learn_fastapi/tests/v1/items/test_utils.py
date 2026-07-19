from io import BytesIO
from typing import Any

import pytest
from fastapi import UploadFile
from pydantic import SecretStr
from starlette.datastructures import Headers

from learn_fastapi.src.constants import CLOUDINARY_ASSET_FOLDER
from learn_fastapi.src.items.infrastructure import image_storage


@pytest.fixture
def cloudinary_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(image_storage.settings, "cloudinary_cloud_name", "test-cloud")
    monkeypatch.setattr(
        image_storage.settings, "cloudinary_api_key", SecretStr("test-key")
    )
    monkeypatch.setattr(
        image_storage.settings, "cloudinary_api_secret", SecretStr("test-secret")
    )


async def test_save_image_file_uses_cloudinary_sdk(
    monkeypatch: pytest.MonkeyPatch,
    cloudinary_settings: None,
) -> None:
    captured: dict[str, Any] = {}

    def fake_config(**kwargs: Any) -> None:
        captured["config"] = kwargs

    def fake_upload(file: BytesIO, **kwargs: Any) -> dict[str, str]:
        captured["file"] = file
        captured["upload"] = kwargs
        return {
            "public_id": "FastAPI-Ecosystem-Lab/media/new",
            "secure_url": "https://res.cloudinary.com/test/image/upload/new.png",
        }

    monkeypatch.setattr(image_storage.cloudinary, "config", fake_config)
    monkeypatch.setattr(image_storage.cloudinary.uploader, "upload", fake_upload)

    image_file = UploadFile(
        file=BytesIO(b"png"),
        filename="product.png",
        headers=Headers({"content-type": "image/png"}),
    )

    storage = image_storage.CloudinaryImageStorage()
    image = await storage.upload(image_file, "Product image")

    assert image.url == "https://res.cloudinary.com/test/image/upload/new.png"
    assert image.public_id == "FastAPI-Ecosystem-Lab/media/new"
    assert image.content_type == "image/png"
    assert captured["config"] == {
        "cloud_name": "test-cloud",
        "api_key": "test-key",
        "api_secret": "test-secret",
        "secure": True,
    }
    assert captured["file"] is image_file.file
    assert captured["upload"]["asset_folder"] == CLOUDINARY_ASSET_FOLDER
    assert captured["upload"]["resource_type"] == "image"
    assert captured["upload"]["timeout"] == image_storage.CLOUDINARY_UPLOAD_TIMEOUT
    assert captured["upload"]["public_id"]


async def test_delete_image_file_uses_cloudinary_sdk(
    monkeypatch: pytest.MonkeyPatch,
    cloudinary_settings: None,
) -> None:
    captured: dict[str, Any] = {}

    def fake_config(**kwargs: Any) -> None:
        captured["config"] = kwargs

    def fake_destroy(public_id: str, **kwargs: Any) -> dict[str, str]:
        captured["public_id"] = public_id
        captured["destroy"] = kwargs
        return {"result": "ok"}

    monkeypatch.setattr(image_storage.cloudinary, "config", fake_config)
    monkeypatch.setattr(image_storage.cloudinary.uploader, "destroy", fake_destroy)

    storage = image_storage.CloudinaryImageStorage()
    assert await storage.delete("FastAPI-Ecosystem-Lab/media/old") is True
    assert captured["public_id"] == "FastAPI-Ecosystem-Lab/media/old"
    assert captured["destroy"] == {"resource_type": "image", "invalidate": True}
    assert captured["config"]["cloud_name"] == "test-cloud"
