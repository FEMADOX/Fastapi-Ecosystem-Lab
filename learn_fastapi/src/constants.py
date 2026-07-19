from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent

STATIC_DIR = PROJECT_DIR / "src" / "static"
CLOUDINARY_ASSET_FOLDER: str = "FastAPI-Ecosystem-Lab/media"
JS_DIR = STATIC_DIR / "js"
