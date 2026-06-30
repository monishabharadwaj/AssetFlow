from __future__ import annotations

import uuid
from datetime import date
from typing import Any

from app.repositories.asset_repository import AssetRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.operations import ReplacementPlanItem, ReplacementPlanResponse
from app.services.prediction_service import get_prediction_cache
from ml.data.type_profiles import get_type_profile

_CLOSING_BY_PRIORITY = {
    "HIGH": "Escalate to capital planning this quarter.",
    "MEDIUM": "Include in next budget cycle.",
    "LOW": "Monitor quarterly; defer capital until health declines further.",
}


def life_health_divergence_score(
    *,
    life_remaining_pct: float,
    health_score: float | None,
) -> float:
    if health_score is None:
        return 0.0
    return max(0.0, life_remaining_pct / 100.0 - health_score)


def count_life_health_divergence(
    items: list[ReplacementPlanItem],
    *,
    life_min: float = 60.0,
    health_max: float = 0.45,
) -> int:
    return sum(
        1
        for i in items
        if i.life_remaining_pct > life_min
        and i.health_score is not None
        and i.health_score < health_max
    )


def _feature_drivers(features: dict[str, Any]) -> list[str]:
    drivers: list[str] = []
    failures = int(features.get("failure_count", 0) or 0)
    if failures >= 1:
        drivers.append(f"{failures} recorded failure{'s' if failures != 1 else ''}")

    days_since = int(features.get("days_since_last_maintenance", 0) or 0)
    if days_since >= 90:
        drivers.append(f"{days_since} days since last service")

    utilization = float(features.get("utilization_rate", 0) or 0)
    if utilization >= 0.65:
        drivers.append(f"utilization at {int(utilization * 100)}%")

    return drivers[:2]


def build_replacement_rationale(
    *,
    asset_name: str,
    type_name: str,
    age_days: int,
    expected_life_days: int,
    health_score: float | None,
    life_remaining_pct: float,
    priority: str,
    features: dict[str, Any] | None = None,
) -> str:
    """Executive-grade replacement rationale with calendar vs operational context."""
    features = features or {}
    age_factor = age_days / max(expected_life_days, 1)
    health_pct = int(health_score * 100) if health_score is not None else None
    drivers = _feature_drivers(features)

    if life_remaining_pct > 60 and health_score is not None and health_score < 0.45:
        lead = (
            f"Operational degradation despite remaining calendar life: {asset_name} ({type_name}) "
            f"shows {health_pct}% predicted health while ~{life_remaining_pct:.0f}% of expected "
            f"service life remains on paper."
        )
    elif life_remaining_pct < 25 or age_factor > 0.75:
        lead = (
            f"Approaching end of expected useful life: {asset_name} ({type_name}) is {age_days} days "
            f"old with ~{life_remaining_pct:.0f}% calendar life remaining."
        )
    elif health_score is not None and health_score < 0.45:
        lead = (
            f"Health-driven refresh recommended: {asset_name} ({type_name}) at {health_pct}% "
            f"predicted health warrants accelerated replacement or major overhaul."
        )
    else:
        lead = (
            f"Lifecycle review: {asset_name} ({type_name}) at {age_days} days old "
            f"(~{life_remaining_pct:.0f}% calendar life remaining"
            + (f", {health_pct}% health" if health_pct is not None else "")
            + ")."
        )

    body_parts: list[str] = []
    if drivers:
        body_parts.append("Drivers: " + "; ".join(drivers) + ".")
    elif health_score is not None and life_remaining_pct > 60 and health_score < 0.55:
        body_parts.append(
            "Condition-based wear exceeds what age alone would suggest — review utilization and service history."
        )

    closing = _CLOSING_BY_PRIORITY.get(priority, _CLOSING_BY_PRIORITY["MEDIUM"])
    return " ".join([lead, *body_parts, closing])


class ReplacementPlanningService:
    def __init__(
        self,
        asset_repository: AssetRepository,
        maintenance_repository: MaintenanceRepository,
    ) -> None:
        self.asset_repository = asset_repository
        self.maintenance_repository = maintenance_repository

    def build_plan(
        self, *, limit: int = 15, department_id: uuid.UUID | None = None
    ) -> ReplacementPlanResponse:
        items: list[ReplacementPlanItem] = []
        cache = get_prediction_cache()
        today = date.today()
        page = 1

        while len(items) < limit * 3:
            assets, total = self.asset_repository.list(
                page=page, page_size=100, is_active=True, department_id=department_id
            )
            if not assets:
                break
            for asset in assets:
                type_name = asset.asset_type.name if asset.asset_type else "Laptop"
                profile = get_type_profile(type_name)
                age_days = max(0, (today - asset.purchase_date).days)
                life_pct = max(0.0, 1.0 - age_days / profile.expected_life_days)

                prediction = cache.get(str(asset.id))
                health_score = prediction.health_score if prediction else None
                features: dict[str, Any] = {}
                if prediction and prediction.prediction_metadata:
                    features = prediction.prediction_metadata.get("input_features", {}) or {}

                replace_score = self._replacement_urgency(
                    age_days=age_days,
                    expected_life=profile.expected_life_days,
                    health_score=health_score,
                )
                if replace_score < 0.35:
                    continue

                months = self._months_until_replace(
                    age_days=age_days,
                    expected_life=profile.expected_life_days,
                    health_score=health_score,
                )
                priority = "HIGH" if replace_score >= 0.7 else "MEDIUM" if replace_score >= 0.5 else "LOW"
                life_remaining_pct = round(life_pct * 100, 1)
                rationale = build_replacement_rationale(
                    asset_name=asset.name,
                    type_name=type_name,
                    age_days=age_days,
                    expected_life_days=profile.expected_life_days,
                    health_score=health_score,
                    life_remaining_pct=life_remaining_pct,
                    priority=priority,
                    features=features,
                )
                items.append(
                    ReplacementPlanItem(
                        asset_id=str(asset.id),
                        asset_tag=asset.asset_tag,
                        asset_name=asset.name,
                        asset_type=type_name,
                        health_score=health_score,
                        age_days=age_days,
                        life_remaining_pct=life_remaining_pct,
                        replace_within_months=months,
                        rationale=rationale,
                        priority=priority,
                    )
                )
            if page * 100 >= total:
                break
            page += 1

        items.sort(
            key=lambda i: (
                -life_health_divergence_score(
                    life_remaining_pct=i.life_remaining_pct,
                    health_score=i.health_score,
                ),
                -self._priority_rank(i.priority),
                i.replace_within_months,
            )
        )
        return ReplacementPlanResponse(items=items[:limit], total=len(items))

    def _replacement_urgency(
        self,
        *,
        age_days: int,
        expected_life: int,
        health_score: float | None,
    ) -> float:
        age_factor = min(1.0, age_days / max(expected_life, 1))
        health_factor = 1.0 - health_score if health_score is not None else 0.3
        return 0.5 * age_factor + 0.5 * health_factor

    def _months_until_replace(
        self,
        *,
        age_days: int,
        expected_life: int,
        health_score: float | None,
    ) -> int:
        remaining_days = max(0, expected_life - age_days)
        if health_score is not None and health_score < 0.4:
            return max(1, min(3, remaining_days // 30 or 1))
        if health_score is not None and health_score < 0.55:
            return max(2, min(6, remaining_days // 30 or 2))
        return max(3, min(24, remaining_days // 30 or 3))

    def _priority_rank(self, priority: str) -> int:
        return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(priority, 0)
