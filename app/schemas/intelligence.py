from __future__ import annotations

import enum
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.explanation import PredictionExplanation


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HealthPredictionResponse(BaseModel):
    asset_id: str
    asset_tag: str | None = None
    asset_name: str | None = None
    health_score: float = Field(ge=0, le=1)
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    model_version: str
    training_dataset: str
    features_used: list[str]
    prediction_metadata: dict[str, Any]
    predicted_at: datetime
    explanation: PredictionExplanation | None = None


class BatchScoreResponse(BaseModel):
    scored: int
    failed: int
    results: list[HealthPredictionResponse]


class HighRiskAssetItem(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    health_score: float
    risk_level: RiskLevel
    predicted_at: datetime


class HighRiskListResponse(BaseModel):
    items: list[HighRiskAssetItem]
    total: int


class PredictOptions(BaseModel):
    persist: bool = False
