from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.operations import (
    CostOptimizationItem,
    DriftAlert,
    MaintenanceWindowSuggestion,
    PipelineStatusResponse,
    ReplacementPlanItem,
)


class ChartPoint(BaseModel):
    label: str
    value: float
    category: str | None = None


class ReportInsightSection(BaseModel):
    key: str
    title: str
    summary: str
    bullets: list[str] = Field(default_factory=list)


class ReplacementPlanEnriched(ReplacementPlanItem):
    why_replace: str
    remaining_useful_life_months: int
    health_trend: str
    maintenance_spend: float
    repair_vs_replace: str
    business_impact_if_delayed: str


class DriftAnalytics(BaseModel):
    alerts: list[DriftAlert]
    deteriorating: list[DriftAlert]
    improving_count: int
    health_trend_chart: list[ChartPoint]
    department_comparison: list[ChartPoint]
    ai_insight: str
    key_factors: list[str]


class CostAnalytics(BaseModel):
    items: list[CostOptimizationItem]
    cost_distribution: list[ChartPoint]
    department_costs: list[ChartPoint]
    estimated_annual_savings: float
    ai_insight: str
    opportunities: list[str]


class ReplacementAnalytics(BaseModel):
    items: list[ReplacementPlanEnriched]
    ai_insight: str


class MaintenanceAnalytics(BaseModel):
    items: list[MaintenanceWindowSuggestion]
    priority_ranking: list[ChartPoint]
    department_workload: list[ChartPoint]
    ai_insight: str
    skip_risk_summary: str


class OrgBenchmarks(BaseModel):
    org_avg_fleet_health_pct: int
    dept_vs_org_health_delta: int
    org_high_risk_assets: int


class ReportsAnalyticsResponse(BaseModel):
    generated_at: datetime
    scope_label: str
    use_ai: bool
    source: str
    ollama_enabled: bool
    benchmarks: OrgBenchmarks | None = None
    kpis: dict[str, int | float | str]
    executive_sections: list[ReportInsightSection]
    drift: DriftAnalytics
    cost: CostAnalytics
    replacement: ReplacementAnalytics
    maintenance: MaintenanceAnalytics
    scoring: PipelineStatusResponse
