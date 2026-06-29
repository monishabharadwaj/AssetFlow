from __future__ import annotations

import uuid

from app.repositories.asset_repository import AssetRepository
from app.schemas.operations import MaintenanceScheduleResponse, MaintenanceWindowSuggestion
from app.services.prediction_service import get_prediction_cache


class MaintenanceSchedulingService:
    def __init__(self, asset_repository: AssetRepository) -> None:
        self.asset_repository = asset_repository

    def suggest_windows(
        self, *, limit: int = 10, department_id: uuid.UUID | None = None
    ) -> MaintenanceScheduleResponse:
        items: list[MaintenanceWindowSuggestion] = []
        cache = get_prediction_cache()
        allowed_ids: set[uuid.UUID] | None = None
        if department_id is not None:
            allowed_ids = self.asset_repository.filter_ids_by_department(
                [uuid.UUID(p.asset_id) for p in cache.values()],
                department_id,
            )

        for prediction in cache.values():
            if allowed_ids is not None and uuid.UUID(prediction.asset_id) not in allowed_ids:
                continue
            features = prediction.prediction_metadata.get("input_features", {})
            utilization = float(features.get("utilization_rate", 0.5))
            days_since = int(features.get("days_since_last_maintenance", 0))

            if prediction.risk_level.value == "LOW" and days_since < 120:
                continue

            window, days_out, rationale = self._suggest_window(
                asset_name=prediction.asset_name or prediction.asset_tag or "Asset",
                utilization=utilization,
                risk_level=prediction.risk_level.value,
                days_since_maint=days_since,
            )
            items.append(
                MaintenanceWindowSuggestion(
                    asset_id=prediction.asset_id,
                    asset_tag=prediction.asset_tag or "",
                    asset_name=prediction.asset_name or "",
                    utilization_rate=round(utilization, 3),
                    suggested_window=window,
                    suggested_within_days=days_out,
                    rationale=rationale,
                )
            )

        items.sort(key=lambda i: (i.suggested_within_days, -i.utilization_rate))
        return MaintenanceScheduleResponse(items=items[:limit], total=len(items))

    def _suggest_window(
        self,
        *,
        asset_name: str,
        utilization: float,
        risk_level: str,
        days_since_maint: int,
    ) -> tuple[str, int, str]:
        if risk_level == "HIGH":
            return (
                "Immediate (within 7 days)",
                7,
                f"{asset_name} is high risk with {days_since_maint} days since last service.",
            )
        if risk_level == "MEDIUM" or utilization > 0.6:
            return (
                "Next 2 weeks",
                14,
                f"Schedule during low-utilization window; utilization at {utilization:.0%}.",
            )
        return (
            "Next month",
            30,
            f"Routine preventive window; {days_since_maint} days since last maintenance.",
        )
