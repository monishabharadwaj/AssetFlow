import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.schemas.common import PaginatedResponse


class EmployeeCreate(BaseModel):
    department_id: uuid.UUID
    employee_code: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    job_title: str | None = Field(default=None, max_length=100)

    @field_validator("employee_code", "first_name", "last_name", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()


class EmployeeUpdate(BaseModel):
    department_id: uuid.UUID | None = None
    employee_code: str | None = Field(default=None, min_length=1, max_length=50)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    job_title: str | None = Field(default=None, max_length=100)
    is_active: bool | None = None

    @field_validator("employee_code", "first_name", "last_name", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @model_validator(mode="after")
    def at_least_one_field(self) -> "EmployeeUpdate":
        if not any(
            field is not None
            for field in (
                self.department_id,
                self.employee_code,
                self.first_name,
                self.last_name,
                self.email,
                self.job_title,
                self.is_active,
            )
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    department_id: uuid.UUID
    employee_code: str
    first_name: str
    last_name: str
    email: str
    job_title: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


EmployeeListResponse = PaginatedResponse[EmployeeResponse]
