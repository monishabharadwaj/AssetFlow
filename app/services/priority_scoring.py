from __future__ import annotations

from app.schemas.recommendation import MaintenanceRecommendation
from ml.data.type_profiles import get_type_profile

# Asset types with higher operational impact (normalized 0-1)
_CRITICALITY_BY_TYPE: dict[str, float] = {
    "Server": 1.0,
    "Production Machine": 0.95,
    "Delivery Van": 0.9,
    "Company Vehicle": 0.85,
    "Networking Device": 0.8,
    "UPS": 0.75,
    "Laptop": 0.55,
    "Desktop Workstation": 0.5,
    "Printer": 0.45,
    "Monitor": 0.4,
    "Conference AV": 0.35,
    "Office Furniture": 0.2,
}


def _asset_criticality(asset_type: str) -> float:
    if asset_type in _CRITICALITY_BY_TYPE:
        return _CRITICALITY_BY_TYPE[asset_type]
    profile = get_type_profile(asset_type)
    return min(1.0, profile.downtime_sensitivity / 1.8)


class PriorityScoringService:
    def compute_score(
        self,
        item: MaintenanceRecommendation,
        *,
        asset_type: str = "Laptop",
        failure_count: int = 0,
        is_ai_high_risk: bool = False,
    ) -> float:
        if item.predicted_health_score > 0:
            health_urgency = 1.0 - item.predicted_health_score
        else:
            health_urgency = 0.5

        overdue_severity = min(item.suggested_within_days / 60.0, 1.0) if item.suggested_within_days > 0 else 0.0
        criticality = _asset_criticality(asset_type)
        failure_component = min(failure_count / 5.0, 1.0)
        confidence_boost = 1.0 if is_ai_high_risk and item.priority.value == "HIGH" else 0.0

        raw = (
            0.35 * health_urgency
            + 0.25 * overdue_severity
            + 0.20 * criticality
            + 0.10 * failure_component
            + 0.10 * confidence_boost
        )
        return round(min(100.0, max(0.0, raw * 100)), 1)

    def rank_recommendations(
        self,
        items: list[MaintenanceRecommendation],
        *,
        asset_types: dict[str, str] | None = None,
        failure_counts: dict[str, int] | None = None,
        ai_high_risk_ids: set[str] | None = None,
    ) -> list[MaintenanceRecommendation]:
        asset_types = asset_types or {}
        failure_counts = failure_counts or {}
        ai_high_risk_ids = ai_high_risk_ids or set()

        scored: list[MaintenanceRecommendation] = []
        for item in items:
            score = self.compute_score(
                item,
                asset_type=asset_types.get(item.asset_id, "Laptop"),
                failure_count=failure_counts.get(item.asset_id, 0),
                is_ai_high_risk=item.asset_id in ai_high_risk_ids,
            )
            scored.append(item.model_copy(update={"priority_score": score}))

        scored.sort(
            key=lambda i: (-i.priority_score, i.predicted_health_score if i.predicted_health_score > 0 else 1.0),
        )
        return scored
