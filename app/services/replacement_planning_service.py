from __future__ import annotations

import uuid
from datetime import date

from app.repositories.asset_repository import AssetRepository
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.operations import ReplacementPlanItem, ReplacementPlanResponse
from app.services.prediction_service import get_prediction_cache
from ml.data.type_profiles import get_type_profile


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

        while len(items) < limit:
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
                rationale = self._rationale(
                    asset_name=asset.name,
                    type_name=type_name,
                    age_days=age_days,
                    health_score=health_score,
                    life_remaining_pct=round(life_pct * 100, 1),
                )
                items.append(
                    ReplacementPlanItem(
                        asset_id=str(asset.id),
                        asset_tag=asset.asset_tag,
                        asset_name=asset.name,
                        asset_type=type_name,
                        health_score=health_score,
                        age_days=age_days,
                        life_remaining_pct=round(life_pct * 100, 1),
                        replace_within_months=months,
                        rationale=rationale,
                        priority=priority,
                    )
                )
            if page * 100 >= total:
                break
            page += 1

        items.sort(key=lambda i: (-self._priority_rank(i.priority), i.replace_within_months))
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
            return max(1, min(3, remaining_days // 30))
        if health_score is not None and health_score < 0.55:
            return max(2, min(6, remaining_days // 30))
        return max(3, min(24, remaining_days // 30))

    def _priority_rank(self, priority: str) -> int:
        return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(priority, 0)

    def _rationale(
        self,
        *,
        asset_name: str,
        type_name: str,
        age_days: int,
        health_score: float | None,
        life_remaining_pct: float,
    ) -> str:
        parts = [
            f"{asset_name} ({type_name}) is {age_days} days old "
            f"with ~{life_remaining_pct:.0f}% expected life remaining."
        ]
        if health_score is not None:
            parts.append(f"AI predicted health is {int(health_score * 100)}%.")
        parts.append("Plan budget for replacement before reliability drops further.")
        return " ".join(parts)
