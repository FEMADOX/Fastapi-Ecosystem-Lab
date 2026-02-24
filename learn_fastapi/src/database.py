import json
from pathlib import Path

from learn_fastapi.src.first_steps.schema import Item

DB_PATH = Path(__file__).parent / "database.json"


def load_db() -> dict[str, Item]:
    with Path.open(DB_PATH) as f:
        raw = json.load(f)
        return {key: Item(**value) for key, value in raw.items()}


def save_db(db: dict[str, Item]) -> None:
    serializable = {}
    for key, value in db.items():
        if not isinstance(value, Item):
            raise ValueError(f"Value for key {key} is not an instance of Item")
        # if value.images:
        #     for image in value.images:
        #         if not isinstance(image.image, bytes):
        #             raise ValueError(f"Image for key {key} is not an instance of bytes")
        #         with Path(f"{image.name}").open("wb") as image_file:
        #             image_file.write(image.image)
        if value.image:
            if not isinstance(value.image.image, bytes):
                raise ValueError(f"Image for key {key} is not an instance of bytes")
            with Path(f"{value.image.name}").open("wb") as image_file:
                image_file.write(value.image.image)
            value.image.url = (
                Path(__file__).parent / "assets" / "images" / value.image.name
            )
        serializable[key] = value.model_dump()

    with Path.open(DB_PATH, "w") as f:
        json.dump(serializable, f, indent=4)
