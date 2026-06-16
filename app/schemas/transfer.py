import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.common import PaginatedResponse


class TransferCreate(BaseModel):
    to_department_id: uuid.UUID
    to_location: str = Field(..., min_length=1, max_length=255)
    transferred_at: datetime
    reason: str | None = None
    performed_by: uuid.UUID | None = None

    @field_validator("to_location", mode="before")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()


class TransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    from_department_id: uuid.UUID
    to_department_id: uuid.UUID
    from_location: str
    to_location: str
    transferred_at: datetime
    reason: str | None
    performed_by: uuid.UUID | None
    created_at: datetime


TransferListResponse = PaginatedResponse[TransferResponse]
