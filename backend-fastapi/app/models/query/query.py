from fastapi import HTTPException

from pydantic import BaseModel, field_validator, RootModel


class AQLVersion(RootModel[str]):
    root: str

    @field_validator("root")
    @classmethod
    def validate_version_format(cls, v):
        parts = v.split(".")
        if len(parts) != 3:
            raise HTTPException(status_code=400, detail=f"Invalid version format: {v}")
        if not all(part.isdigit() for part in parts):
            raise HTTPException(status_code=400, detail=f"Invalid version format: {v}")
        return v


class AQLName(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v):
        if not v:
            raise HTTPException(status_code=400, detail="Name cannot be empty")

        namesplit = v.split("::")
        if len(namesplit) != 2:
            raise HTTPException(
                status_code=400,
                detail="Invalid name format. Must be like org.ehrbase.local::myquery",
            )
        name0split = namesplit[0].split(".")
        if len(name0split) != 3:
            raise HTTPException(
                status_code=400,
                detail="Invalid name format. Must be like org.ehrbase.local::myquery",
            )
        name1split = namesplit[1].split(".")
        if len(name1split) != 1:
            raise HTTPException(
                status_code=400,
                detail="Invalid name format. Must be like org.ehrbase.local::myquery",
            )
        return v
