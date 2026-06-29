from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    employee_id: UUID
    email: str
    full_name: str
    employee_code: str
    job_title: str | None = None
    department_id: UUID
    department_name: str


class UserCreate(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER
    employee_id: UUID | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    employee_code: str | None = Field(default=None, min_length=1, max_length=50)
    department_id: UUID | None = None
    job_title: str | None = Field(default=None, max_length=100)

    @model_validator(mode="after")
    def validate_employee_source(self) -> "UserCreate":
        if self.employee_id is None:
            missing = [
                name
                for name, value in (
                    ("first_name", self.first_name),
                    ("last_name", self.last_name),
                    ("email", self.email),
                    ("employee_code", self.employee_code),
                    ("department_id", self.department_id),
                )
                if value is None
            ]
            if missing:
                raise ValueError(
                    "Provide employee_id or all of: first_name, last_name, email, employee_code, department_id"
                )
        return self
