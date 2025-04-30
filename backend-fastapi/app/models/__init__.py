from pydantic import BaseModel, field_validator
from uuid import UUID
from enum import Enum


class VersionedObjectId(BaseModel):
    versionedId: str

    def __init__(self, value: str):
        try:
            uuid_str, text, number = value.split("::")
            # Validate UUID
            UUID(uuid_str)
            # Validate integer
            number = int(number)
        except ValueError:
            raise ValueError("VersionID must be in the format 'UUID::string::int'")
        super().__init__(versionedId=value)
        self.versionedId = value

    def __str__(self):
        return self.versionedId


class formatEnum(str, Enum):
    json = "json"
    xml = "xml"
    flat = "flat"
    structured = "structured"
