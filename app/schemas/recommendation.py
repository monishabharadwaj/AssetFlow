from __future__ import annotations

import enum
from datetime import date, timedelta

from pydantic import BaseModel


class RecommendationPriority(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MaintenanceRecommendation(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    asset_type_name: str | None = None
    department_name: str | None = None
    title: str
    priority: RecommendationPriority
    maintenance_type: str
    suggested_within_days: int
    rationale: str
    risk_level: str
    predicted_health_score: float


class RecommendationListResponse(BaseModel):
    items: list[MaintenanceRecommendation]
    total: int
