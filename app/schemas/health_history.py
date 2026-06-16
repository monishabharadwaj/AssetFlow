import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import PaginatedResponse


class HealthHistoryCreate(BaseModel):
    recorded_at: datetime | None = None
    health_score: Decimal | None = Field(default=None, ge=0, le=1)
    condition_rating: int | None = Field(default=None, ge=1, le=10)
    operational_hours: Decimal | None = Field(default=None, ge=0)
    failure_count: int = Field(default=0, ge=0)
    days_since_last_maintenance: int | None = Field(default=None, ge=0)
    age_in_days: int | None = Field(default=None, ge=0)
    depreciation_ratio: Decimal | None = Field(default=None, ge=0, le=1)
    raw_features: dict[str, Any] | None = None
    prediction_metadata: dict[str, Any] | None = None
    notes: str | None = None


class HealthHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    asset_id: uuid.UUID
    recorded_at: datetime
    health_score: Decimal | None
    condition_rating: int | None
    operational_hours: Decimal | None
    failure_count: int
    days_since_last_maintenance: int | None
    age_in_days: int | None
    depreciation_ratio: Decimal | None
    raw_features: dict[str, Any] | None
    prediction_metadata: dict[str, Any] | None
    notes: str | None
    created_at: datetime


HealthHistoryListResponse = PaginatedResponse[HealthHistoryResponse]
