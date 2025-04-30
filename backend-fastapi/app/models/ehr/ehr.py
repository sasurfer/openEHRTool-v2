from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from app.models import VersionedObjectId, formatEnum


class EhrStatusRequest(BaseModel):
    ehrstatus: str


class EhrStatusPost(EhrStatusRequest):
    pass


class EhrStatusGetPut(EhrStatusRequest):
    ehrid: UUID
    ehrstatusVersionedId: VersionedObjectId

    @field_validator("ehrstatusVersionedId", mode="before")
    @classmethod
    def validate_custom_field(cls, v):
        return VersionedObjectId(v)


class DirectoryRequest(BaseModel):
    directory: str


class DirectoryPost(DirectoryRequest):
    pass


class DirectoryPut(DirectoryRequest):
    directoryVersionedId: VersionedObjectId

    @field_validator("directoryVersionedId", mode="before")
    @classmethod
    def validate_custom_field(cls, v):
        return VersionedObjectId(v)


class DirectoryDelete(BaseModel):
    directoryVersionedId: VersionedObjectId

    @field_validator("directoryVersionedId", mode="before")
    @classmethod
    def validate_custom_field(cls, v):
        return VersionedObjectId(v)


def get_ehr_enum_value(value: str) -> formatEnum:
    for item in formatEnum:
        if item.value.lower() == value.lower():
            return value.lower()
    raise HTTPException(status_code=400, detail=f"Invalid enum value: {value}")
