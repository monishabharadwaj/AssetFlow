import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.core.access_scope import AccessContext
from app.core.enums import UserRole
from app.schemas.dashboard import DashboardSummaryResponse
from app.schemas.intelligence import HealthPredictionResponse, RiskLevel
from app.schemas.operations import CostOptimizationItem, MaintenanceWindowSuggestion
from app.schemas.recommendation import MaintenanceRecommendation, RecommendationListResponse, RecommendationPriority
from app.schemas.reports_analytics import (
    ChartPoint,
    CostAnalytics,
    DriftAnalytics,
    MaintenanceAnalytics,
    ReplacementAnalytics,
    ReplacementPlanEnriched,
)
from app.services.reports_analytics_service import ReportsAnalyticsService, compute_org_benchmarks


def _prediction(asset_id: uuid.UUID, health: float, risk: RiskLevel) -> HealthPredictionResponse:
    return HealthPredictionResponse(
        asset_id=str(asset_id),
        asset_tag=f"TAG-{str(asset_id)[:8]}",
        health_score=health,
        risk_level=risk,
        confidence=0.9,
        model_version="test",
        training_dataset="test",
        features_used=[],
        prediction_metadata={},
        predicted_at=datetime.now(timezone.utc),
    )


def test_compute_org_benchmarks_for_department_scope() -> None:
    dept_a = uuid.uuid4()
    predictions = [
        _prediction(uuid.uuid4(), 0.8, RiskLevel.LOW),
        _prediction(uuid.uuid4(), 0.6, RiskLevel.MEDIUM),
        _prediction(uuid.uuid4(), 0.2, RiskLevel.HIGH),
        _prediction(uuid.uuid4(), 0.4, RiskLevel.HIGH),
    ]
    viewer = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.VIEWER,
        department_id=dept_a,
    )

    result = compute_org_benchmarks(viewer, dept_avg_health_pct=80, all_predictions=predictions)

    assert result is not None
    assert result.org_avg_fleet_health_pct == 50
    assert result.dept_vs_org_health_delta == 30
    assert result.org_high_risk_assets == 2


def test_compute_org_benchmarks_none_for_admin() -> None:
    admin = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.ADMIN,
        department_id=uuid.uuid4(),
    )
    predictions = [_prediction(uuid.uuid4(), 0.7, RiskLevel.LOW)]

    assert compute_org_benchmarks(admin, dept_avg_health_pct=70, all_predictions=predictions) is None


def test_scoped_predictions_filters_by_department() -> None:
    dept_a = uuid.uuid4()
    asset_a = uuid.uuid4()
    asset_b = uuid.uuid4()
    cache = {
        str(asset_a): _prediction(asset_a, 0.9, RiskLevel.LOW),
        str(asset_b): _prediction(asset_b, 0.3, RiskLevel.HIGH),
    }

    asset_repository = MagicMock()
    asset_repository.filter_ids_by_department.return_value = {asset_a}

    service = ReportsAnalyticsService(
        dashboard_service=MagicMock(),
        recommendation_service=MagicMock(),
        drift_service=MagicMock(),
        replacement_service=MagicMock(),
        cost_service=MagicMock(),
        maintenance_service=MagicMock(),
        pipeline_service=MagicMock(),
        asset_repository=asset_repository,
        maintenance_repository=MagicMock(),
    )

    viewer = AccessContext(
        user_id=uuid.uuid4(),
        employee_id=uuid.uuid4(),
        role=UserRole.VIEWER,
        department_id=dept_a,
    )

    with patch("app.services.reports_analytics_service.get_prediction_cache", return_value=cache):
        scoped = service._scoped_predictions(viewer)

    scoped_ids = {p.asset_id for p in scoped}
    assert scoped_ids == {str(asset_a)}
    assert str(asset_b) not in scoped_ids


def _replacement_enriched(
    tag: str,
    *,
    life_pct: float = 70.0,
    health: float = 0.3,
    priority: str = "HIGH",
) -> ReplacementPlanEnriched:
    return ReplacementPlanEnriched(
        asset_id=str(uuid.uuid4()),
        asset_tag=tag,
        asset_name=f"Asset {tag}",
        asset_type="Laptop",
        health_score=health,
        age_days=120,
        life_remaining_pct=life_pct,
        replace_within_months=6,
        rationale="Operational degradation despite remaining calendar life.",
        priority=priority,
        why_replace="Why replace",
        remaining_useful_life_months=6,
        health_trend="declining",
        maintenance_spend=150.0,
        repair_vs_replace="Repair vs replace technical detail",
        business_impact_if_delayed="Delay increases downtime risk",
    )


def _executive_fixture(*, divergence_items: int = 2) -> tuple:
    summary = DashboardSummaryResponse(
        total_assets=400,
        total_active_assets=400,
        total_employees=50,
        total_active_employees=50,
        total_departments=5,
        total_active_departments=5,
        assets_by_status=[],
        assets_by_department=[],
        maintenance_due_count=12,
        recent_activity=[],
    )
    predictions = [
        _prediction(uuid.uuid4(), 0.78, RiskLevel.LOW),
        _prediction(uuid.uuid4(), 0.2, RiskLevel.HIGH),
    ]
    recs = RecommendationListResponse(items=[], total=0)
    drift = DriftAnalytics(
        alerts=[],
        deteriorating=[],
        improving_count=3,
        health_trend_chart=[],
        department_comparison=[
            ChartPoint(label="Engineering", value=85.0),
            ChartPoint(label="Operations", value=62.0),
        ],
        ai_insight="Drift stable",
        key_factors=["utilization"],
    )
    cost = CostAnalytics(
        items=[],
        cost_distribution=[],
        department_costs=[],
        estimated_annual_savings=25_000.0,
        ai_insight="Savings available",
        opportunities=["Reduce TCO on aging laptops"],
    )
    replacement_items = [_replacement_enriched(f"IT-LAP-{i:03d}") for i in range(divergence_items)]
    replacement = ReplacementAnalytics(items=replacement_items, ai_insight="Capital review")
    maintenance = MaintenanceAnalytics(
        items=[],
        priority_ranking=[],
        department_workload=[],
        ai_insight="Schedule on track",
        skip_risk_summary="Low skip risk",
    )
    kpis = {
        "active_assets": 400,
        "high_risk_assets": 15,
        "maintenance_due": 12,
        "avg_fleet_health_pct": 78,
        "estimated_annual_savings": 25_000.0,
    }
    return summary, predictions, recs, drift, cost, replacement, maintenance, kpis


def test_executive_summary_mentions_divergence_count() -> None:
    service = ReportsAnalyticsService(
        dashboard_service=MagicMock(),
        recommendation_service=MagicMock(),
        drift_service=MagicMock(),
        replacement_service=MagicMock(),
        cost_service=MagicMock(),
        maintenance_service=MagicMock(),
        pipeline_service=MagicMock(),
        asset_repository=MagicMock(),
        maintenance_repository=MagicMock(),
    )
    summary, predictions, recs, drift, cost, replacement, maintenance, kpis = _executive_fixture(
        divergence_items=3,
    )

    sections = service._build_executive_sections(
        summary=summary,
        predictions=predictions,
        recs=recs,
        drift=drift,
        cost=cost,
        replacement=replacement,
        maintenance=maintenance,
        kpis=kpis,
    )

    exec_section = next(s for s in sections if s.key == "executive_summary")
    assert "3 assets show high calendar life but critically low operational health" in exec_section.summary


def test_executive_sections_limit_kpi_repetition() -> None:
    service = ReportsAnalyticsService(
        dashboard_service=MagicMock(),
        recommendation_service=MagicMock(),
        drift_service=MagicMock(),
        replacement_service=MagicMock(),
        cost_service=MagicMock(),
        maintenance_service=MagicMock(),
        pipeline_service=MagicMock(),
        asset_repository=MagicMock(),
        maintenance_repository=MagicMock(),
    )
    summary, predictions, recs, drift, cost, replacement, maintenance, kpis = _executive_fixture()

    sections = service._build_executive_sections(
        summary=summary,
        predictions=predictions,
        recs=recs,
        drift=drift,
        cost=cost,
        replacement=replacement,
        maintenance=maintenance,
        kpis=kpis,
    )

    all_text = " ".join(s.summary + " " + " ".join(s.bullets) for s in sections)
    assert all_text.count("400 active assets") <= 2
    assert all_text.count("78% health") <= 2
    assert all_text.count("15 high-risk") <= 2


def test_build_prioritized_actions_dedupes_by_asset_tag() -> None:
    shared_tag = "IT-LAP-099"
    recs = RecommendationListResponse(
        items=[
            MaintenanceRecommendation(
                asset_id=str(uuid.uuid4()),
                asset_tag=shared_tag,
                asset_name="Shared asset",
                title="Urgent service",
                priority=RecommendationPriority.HIGH,
                maintenance_type="preventive",
                suggested_within_days=7,
                rationale="Overdue",
                risk_level="HIGH",
                predicted_health_score=0.2,
            )
        ],
        total=1,
    )
    replacement = ReplacementAnalytics(
        items=[_replacement_enriched(shared_tag, priority="HIGH")],
        ai_insight="",
    )
    cost = CostAnalytics(
        items=[
            CostOptimizationItem(
                asset_id=str(uuid.uuid4()),
                asset_tag=shared_tag,
                asset_name="Shared asset",
                purchase_cost=800.0,
                maintenance_spend=1200.0,
                tco_ratio=1.5,
                recommendation="Review TCO",
                priority="HIGH",
            )
        ],
        cost_distribution=[],
        department_costs=[],
        estimated_annual_savings=5000.0,
        ai_insight="",
        opportunities=[],
    )
    maintenance = MaintenanceAnalytics(
        items=[
            MaintenanceWindowSuggestion(
                asset_id=str(uuid.uuid4()),
                asset_tag=shared_tag,
                asset_name="Shared asset",
                utilization_rate=0.8,
                suggested_window="next week",
                suggested_within_days=5,
                rationale="High utilization",
            )
        ],
        priority_ranking=[],
        department_workload=[],
        ai_insight="",
        skip_risk_summary="",
    )

    actions = ReportsAnalyticsService._build_prioritized_actions(recs, replacement, cost, maintenance)

    tag_hits = [a for a in actions if shared_tag in a]
    assert len(tag_hits) == 1
