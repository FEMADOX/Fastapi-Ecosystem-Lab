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
            msg = f"Value for key {key} is not an instance of Item"
            raise TypeError(msg)
        serializable[key] = value.model_dump()

    with Path.open(DB_PATH, "w") as f:
        json.dump(serializable, f, indent=4)
