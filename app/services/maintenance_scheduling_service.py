from __future__ import annotations

from app.schemas.operations import MaintenanceScheduleResponse, MaintenanceWindowSuggestion
from app.services.prediction_service import get_prediction_cache


class MaintenanceSchedulingService:
    def suggest_windows(self, *, limit: int = 10) -> MaintenanceScheduleResponse:
        items: list[MaintenanceWindowSuggestion] = []
        cache = get_prediction_cache()

        for prediction in cache.values():
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
                "Next available low-traffic window (within 3–5 days)",
                5,
                f"{asset_name} is high risk with {int(utilization * 100)}% utilization — "
                f"schedule urgent service during off-peak hours.",
            )
        if utilization > 0.8:
            return (
                "Weekend or after-hours slot",
                14,
                f"{asset_name} runs at {int(utilization * 100)}% utilization — "
                f"avoid weekday downtime; book a low-load maintenance window.",
            )
        if days_since_maint > 180:
            return (
                "Standard business-hours slot",
                10,
                f"{asset_name} is due for service ({days_since_maint} days since last maintenance) "
                f"and can be serviced during normal hours.",
            )
        return (
            "Flexible — next 2–3 weeks",
            21,
            f"{asset_name} has moderate utilization ({int(utilization * 100)}%) — "
            f"plan preventive maintenance in the next maintenance cycle.",
        )
