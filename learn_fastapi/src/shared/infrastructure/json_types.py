from collections.abc import Mapping, Sequence
from typing import cast

from pydantic import BaseModel

type JSONPrimitive = str | int | float | bool | None
type JSONValue = JSONPrimitive | Sequence[JSONValue] | Mapping[str, JSONValue]
type JSONObject = Mapping[str, JSONValue]


def model_dump_json_object(
    model: BaseModel,
    *,
    include: set[str] | None = None,
) -> JSONObject:
    """Serialize a Pydantic model object to a JSON object.

    Returns:
        Casted dictionary representation of the model object.

    """
    return cast(
        "JSONObject",
        model.model_dump(mode="json", include=include),
    )
