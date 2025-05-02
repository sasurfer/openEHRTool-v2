from fastapi import HTTPException

from pydantic import BaseModel
from app.models import formatEnum
from app.models import VersionedObjectId


class CompositionRequest(BaseModel):
    composition: str


class CompositionPost(CompositionRequest):
    pass


def get_composition_enum_value(value: str) -> formatEnum:
    for item in formatEnum:
        if item.value.lower() == value.lower():
            return value.lower()
    raise HTTPException(
        status_code=400, detail=f"Invalid composition enum value: {value}"
    )
