import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AllocationAction
from app.schemas.common import PaginatedResponse


class AllocationAssignRequest(BaseModel):
    employee_id: uuid.UUID
    allocated_at: datetime
    notes: str | None = None
    performed_by: uuid.UUID | None = None


class AllocationReturnRequest(BaseModel):
    returned_at: datetime
    notes: str | None = None
    performed_by: uuid.UUID | None = None


class AllocationReassignRequest(BaseModel):
    employee_id: uuid.UUID
    allocated_at: datetime
    notes: str | None = None
    performed_by: uuid.UUID | None = None


class AllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    employee_id: uuid.UUID
    action: AllocationAction
    allocated_at: datetime
    returned_at: datetime | None
    notes: str | None
    performed_by: uuid.UUID | None
    created_at: datetime


AllocationListResponse = PaginatedResponse[AllocationResponse]
