from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import NotificationSeverity, NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    notification_type: NotificationType
    severity: NotificationSeverity
    title: str
    message: str
    asset_id: uuid.UUID | None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int


class PipelineRunResponse(BaseModel):
    scored: int
    failed: int
    notifications_created: int
    maintenance_auto_scheduled: int
    drift_alerts: int
    ran_at: datetime


class PipelineStatusResponse(BaseModel):
    scheduler_enabled: bool
    scheduler_interval_minutes: int
    last_run_at: datetime | None
    cache_warm: bool
    scored_assets: int
    policy_automation_enabled: bool


class DriftAlert(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    previous_health: float
    current_health: float
    health_delta: float
    message: str


class DriftStatusResponse(BaseModel):
    alerts: list[DriftAlert]
    total: int


class ReplacementPlanItem(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    asset_type: str
    health_score: float | None
    age_days: int
    life_remaining_pct: float
    replace_within_months: int
    rationale: str
    priority: str


class ReplacementPlanResponse(BaseModel):
    items: list[ReplacementPlanItem]
    total: int


class CostOptimizationItem(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    purchase_cost: float
    maintenance_spend: float
    tco_ratio: float
    recommendation: str
    priority: str


class CostOptimizationResponse(BaseModel):
    items: list[CostOptimizationItem]
    total: int


class MaintenanceWindowSuggestion(BaseModel):
    asset_id: str
    asset_tag: str
    asset_name: str
    utilization_rate: float
    suggested_window: str
    suggested_within_days: int
    rationale: str


class MaintenanceScheduleResponse(BaseModel):
    items: list[MaintenanceWindowSuggestion]
    total: int


class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str


class KnowledgeGraphResponse(BaseModel):
    center_id: str
    center_type: str
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class OperationalReportResponse(BaseModel):
    title: str
    generated_at: datetime
    summary: str
    sections: list[str]
    source: str = Field(description="template or ollama")
    metrics: dict[str, int | float | str]
