from __future__ import annotations

import enum

from pydantic import BaseModel, Field


class FactorSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ExplanationFactor(BaseModel):
    factor: str
    severity: FactorSeverity
    message: str


class EnterpriseHealthBrief(BaseModel):
    what_happened: str
    why_predicted: str
    business_impact: str
    recommended_action: str
    priority: str
    estimated_downtime: str
    estimated_effort: str
    estimated_cost: str | None = None
    health_band: str
    confidence_label: str
    remaining_useful_life: str | None = None
    is_improvement: bool = False


class PredictionExplanation(BaseModel):
    anomaly_detected: bool
    health_delta: float | None = None
    previous_health_score: float | None = None
    factors: list[ExplanationFactor] = Field(default_factory=list)
    summary: str
    enterprise_brief: EnterpriseHealthBrief | None = None


class RootCauseResponse(BaseModel):
    asset_id: str
    asset_tag: str | None = None
    asset_name: str | None = None
    health_score: float
    risk_level: str
    root_cause_summary: str
    source: str = Field(description="template or ollama")
    factors: list[ExplanationFactor] = Field(default_factory=list)
    anomaly_detected: bool = False
    enterprise_brief: EnterpriseHealthBrief | None = None
