import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import MaintenanceStatus, MaintenanceType
from app.schemas.common import PaginatedResponse


class MaintenanceCreate(BaseModel):
    maintenance_type: MaintenanceType
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    scheduled_date: date | None = None
    completed_date: date | None = None
    cost: Decimal | None = Field(default=None, ge=0)
    description: str = Field(..., min_length=1)
    service_provider: str | None = Field(default=None, max_length=200)
    performed_by: uuid.UUID | None = None


class MaintenanceUpdate(BaseModel):
    maintenance_type: MaintenanceType | None = None
    status: MaintenanceStatus | None = None
    scheduled_date: date | None = None
    completed_date: date | None = None
    cost: Decimal | None = Field(default=None, ge=0)
    description: str | None = Field(default=None, min_length=1)
    service_provider: str | None = Field(default=None, max_length=200)
    performed_by: uuid.UUID | None = None

    @model_validator(mode="after")
    def at_least_one_field(self) -> "MaintenanceUpdate":
        if not any(
            field is not None
            for field in (
                self.maintenance_type,
                self.status,
                self.scheduled_date,
                self.completed_date,
                self.cost,
                self.description,
                self.service_provider,
                self.performed_by,
            )
        ):
            raise ValueError("At least one field must be provided for update")
        return self


class MaintenanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    maintenance_type: MaintenanceType
    status: MaintenanceStatus
    scheduled_date: date | None
    completed_date: date | None
    cost: Decimal | None
    description: str
    service_provider: str | None
    performed_by: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


MaintenanceListResponse = PaginatedResponse[MaintenanceResponse]
