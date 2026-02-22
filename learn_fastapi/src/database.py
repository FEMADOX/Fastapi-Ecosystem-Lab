import json
from pathlib import Path

from learn_fastapi.src.first_steps.schema import Item

DB_PATH = Path(__file__).parent / "database.json"


def load_db() -> dict[str, Item]:
    with Path.open(DB_PATH) as f:
        raw = json.load(f)
        return {key: Item(**value) for key, value in raw.items()}


def save_db(db: dict[str, Item]) -> None:
    with Path.open(DB_PATH, "w") as f:
        json.dump({key: value.model_dump() for key, value in db.items()}, f, indent=4)
