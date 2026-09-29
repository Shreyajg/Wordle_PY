from typing import Any

from bson import ObjectId
from bson.errors import InvalidId


def to_object_id(value: str) -> Any:
    """Spring Data stores String ids as ObjectId when they are valid hex ids."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        return value
