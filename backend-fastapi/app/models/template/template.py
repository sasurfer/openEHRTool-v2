from fastapi import HTTPException

# from pydantic import BaseModel, field_validator
# from typing import Optional
# from uuid import UUID
# from app.models import VersionedObjectId
from enum import Enum

from pydantic import BaseModel


class templateFormatEnum(str, Enum):
    webtemplate = "webtemplate"
    opt = "opt"


def get_template_enum_value(value: str) -> templateFormatEnum:
    for item in templateFormatEnum:
        if item.value.lower() == value.lower():
            return value.lower()
    raise HTTPException(status_code=400, detail=f"Invalid template enum value: {value}")


class TemplateRequest(BaseModel):
    template: str


class TemplatePost(TemplateRequest):
    pass
