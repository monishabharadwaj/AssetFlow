import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.enums import AssetStatus
from app.schemas.common import PaginatedResponse


class AssetCategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class AssetTypeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class AssetCreate(BaseModel):
    asset_tag: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    asset_type_id: uuid.UUID
    purchase_date: date
    purchase_cost: Decimal = Field(..., ge=0)
    current_location: str = Field(default="Unassigned", max_length=255)
    current_department_id: uuid.UUID
    serial_number: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    warranty_expiry: date | None = None

    @field_validator("asset_tag", "name", "current_location", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()


class AssetUpdate(BaseModel):
    asset_tag: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    asset_type_id: uuid.UUID | None = None
    purchase_date: date | None = None
    purchase_cost: Decimal | None = Field(default=None, ge=0)
    current_status: AssetStatus | None = None
    current_location: str | None = Field(default=None, max_length=255)
    current_department_id: uuid.UUID | None = None
    serial_number: str | None = Field(default=None, max_length=100)
    manufacturer: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    warranty_expiry: date | None = None
    is_active: bool | None = None

    @field_validator("asset_tag", "name", "current_location", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return value.strip()

    @model_validator(mode="after")
    def at_least_one_field(self) -> "AssetUpdate":
        if not any(
            field is not None
            for field in (
                self.asset_tag,
                self.name,
                self.asset_type_id,
                self.purchase_date,
                self.purchase_cost,
                self.current_status,
                self.current_location,
                self.current_department_id,
                self.serial_number,
                self.manufacturer,
                self.model,
                self.warranty_expiry,
                self.is_active,
            )
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_tag: str
    name: str
    asset_type_id: uuid.UUID
    purchase_date: date
    purchase_cost: Decimal
    current_status: AssetStatus
    current_location: str
    current_department_id: uuid.UUID
    current_assigned_employee_id: uuid.UUID | None
    serial_number: str | None
    manufacturer: str | None
    model: str | None
    warranty_expiry: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


AssetListResponse = PaginatedResponse[AssetResponse]
