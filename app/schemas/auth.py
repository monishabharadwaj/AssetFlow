from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.core.enums import UserRole
from app.core.password_policy import validate_password_strength


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    must_change_password: bool = False


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool
    must_change_password: bool
    created_at: datetime
    employee_id: UUID
    email: str
    full_name: str
    employee_code: str
    job_title: str | None = None
    department_id: UUID
    department_name: str


class UserCreate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
    role: UserRole = UserRole.VIEWER
    employee_id: UUID | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    employee_code: str | None = Field(default=None, min_length=1, max_length=50)
    department_id: UUID | None = None
    job_title: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        validate_password_strength(value)
        return value

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


class UserCreateResponse(UserResponse):
    temporary_password: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        validate_password_strength(value)
        return value


class UserAdminUpdate(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserAdminUpdate":
        if self.role is None and self.is_active is None:
            raise ValueError("At least one field must be provided")
        return self


class PasswordResetResponse(BaseModel):
    user: UserResponse
    temporary_password: str
