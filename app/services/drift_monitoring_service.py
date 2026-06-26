from __future__ import annotations

from app.core.config import settings
from app.core.health_thresholds import should_notify_drift
from app.repositories.health_history_repository import HealthHistoryRepository
from app.schemas.intelligence import HealthPredictionResponse
from app.schemas.operations import DriftAlert, DriftStatusResponse
from app.services.prediction_service import get_prediction_cache


class DriftMonitoringService:
    def __init__(self, health_history_repository: HealthHistoryRepository) -> None:
        self.health_history_repository = health_history_repository

    def detect_drift(self, *, threshold: float | None = None) -> DriftStatusResponse:
        min_drop = threshold if threshold is not None else settings.drift_min_drop
        alerts: list[DriftAlert] = []
        cache = get_prediction_cache()

        for prediction in cache.values():
            alert = self._check_prediction_drift(prediction, min_drop=min_drop)
            if alert is not None:
                alerts.append(alert)

        alerts.sort(key=lambda a: a.health_delta)
        return DriftStatusResponse(alerts=alerts, total=len(alerts))

    def _check_prediction_drift(
        self,
        prediction: HealthPredictionResponse,
        *,
        min_drop: float,
    ) -> DriftAlert | None:
        import uuid

        asset_id = uuid.UUID(prediction.asset_id)
        previous = self.health_history_repository.get_latest_for_asset(asset_id)
        if previous is None or previous.health_score is None:
            if prediction.explanation and prediction.explanation.health_delta is not None:
                delta = prediction.explanation.health_delta
                previous_health = 1.0 + delta
                current_health = prediction.health_score
                if not should_notify_drift(
                    previous_health=previous_health,
                    current_health=current_health,
                    min_drop=min_drop,
                    severe_drop=settings.drift_severe_drop,
                    healthy_floor=settings.drift_healthy_floor,
                    notify_below=settings.drift_notify_below,
                ):
                    return None
                if delta <= -min_drop:
                    return self._build_alert(prediction, previous_health=previous_health, delta=delta)
            return None

        previous_health = float(previous.health_score)
        current_health = prediction.health_score
        delta = current_health - previous_health
        if not should_notify_drift(
            previous_health=previous_health,
            current_health=current_health,
            min_drop=min_drop,
            severe_drop=settings.drift_severe_drop,
            healthy_floor=settings.drift_healthy_floor,
            notify_below=settings.drift_notify_below,
        ):
            return None

        return self._build_alert(prediction, previous_health=previous_health, delta=delta)

    def _build_alert(
        self,
        prediction: HealthPredictionResponse,
        *,
        previous_health: float,
        delta: float,
    ) -> DriftAlert:
        asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
        pct_drop = int(abs(delta) * 100)
        return DriftAlert(
            asset_id=prediction.asset_id,
            asset_tag=prediction.asset_tag or "",
            asset_name=asset_name,
            previous_health=round(previous_health, 3),
            current_health=round(prediction.health_score, 3),
            health_delta=round(delta, 3),
            message=(
                f"{asset_name} health dropped {pct_drop}% since last assessment "
                f"({int(previous_health * 100)}% → {int(prediction.health_score * 100)}%)."
            ),
        )
