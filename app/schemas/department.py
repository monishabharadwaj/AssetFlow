import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.common import PaginatedResponse

CODE_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: str | None = None

    @field_validator("name", "code", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not CODE_PATTERN.match(value):
            raise ValueError("code must contain only letters, numbers, underscores, or hyphens")
        return value


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=20)
    description: str | None = None
    is_active: bool | None = None

    @field_validator("name", "code", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not CODE_PATTERN.match(value):
            raise ValueError("code must contain only letters, numbers, underscores, or hyphens")
        return value

    @model_validator(mode="after")
    def at_least_one_field(self) -> "DepartmentUpdate":
        if not any(
            field is not None
            for field in (self.name, self.code, self.description, self.is_active)
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


DepartmentListResponse = PaginatedResponse[DepartmentResponse]
