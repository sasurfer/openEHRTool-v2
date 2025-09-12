from fastapi import HTTPException

from pydantic import BaseModel
from enum import Enum
from app.models import VersionedObjectId


class contributionFormatEnum(str, Enum):
    json = "json"
    xml = "xml"


class ContributionRequest(BaseModel):
    contribution: str


class ContributionPost(ContributionRequest):
    pass


def get_contribution_enum_value(value: str) -> contributionFormatEnum:
    for item in contributionFormatEnum:
        if item.value.lower() == value.lower():
            return value.lower()
    raise HTTPException(
        status_code=400, detail=f"Invalid contribution enum value: {value}"
    )
