import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.core.access_scope import AccessContext
from app.core.enums import UserRole
from app.schemas.intelligence import HealthPredictionResponse, RiskLevel
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
