from __future__ import annotations

import uuid
from datetime import date

from app.core.access_scope import AccessContext
from app.repositories.asset_repository import AssetRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.recommendation import (
    MaintenanceRecommendation,
    RecommendationListResponse,
    RecommendationPriority,
)
from app.services import narrative as narr
from app.services.prediction_service import PredictionService

# Asset types old enough to justify replacement over repair when health collapses.
_REPLACEMENT_AGE_DAYS = 480


class RecommendationService:
    def __init__(
        self,
        prediction_service: PredictionService,
        dashboard_repository: DashboardRepository,
        asset_repository: AssetRepository,
    ) -> None:
        self.prediction_service = prediction_service
        self.dashboard_repository = dashboard_repository
        self.asset_repository = asset_repository

    def _prediction_recommendation(self, prediction) -> MaintenanceRecommendation | None:
        """Derive a single, diverse recommendation from a health prediction."""
        health = prediction.health_score
        health_pct = int(health * 100)
        asset_tag = prediction.asset_tag or ""
        asset_type = prediction.asset_type_name
        department = prediction.department_name
        meta = prediction.prediction_metadata or {}
        features = meta.get("input_features", {})
        age_days = int(features.get("asset_age_days", 0) or 0)
        utilization = float(features.get("utilization_rate", 0) or 0)
        failures = int(features.get("failure_count", 0) or 0)

        base = dict(
            asset_id=prediction.asset_id,
            asset_tag=asset_tag,
            asset_name=prediction.asset_name or asset_tag,
            asset_type_name=asset_type,
            department_name=department,
            predicted_health_score=health,
        )

        # Critical + aging → replacement over repair.
        if health < 0.40 and age_days >= _REPLACEMENT_AGE_DAYS:
            return MaintenanceRecommendation(
                **base,
                title=narr.recommendation_card_title_category(asset_tag, category="REPLACEMENT"),
                priority=RecommendationPriority.HIGH,
                maintenance_type="REPLACEMENT",
                suggested_within_days=30,
                rationale=narr.recommendation_rationale_replacement(
                    asset_tag=asset_tag, asset_type=asset_type,
                    department_name=department, health_pct=health_pct,
                ),
                risk_level="HIGH",
            )

        # High risk → urgent preventive maintenance.
        if health < 0.50:
            return MaintenanceRecommendation(
                **base,
                title=narr.recommendation_card_title(
                    asset_tag, maintenance_type="PREVENTIVE", urgent_health=True
                ),
                priority=RecommendationPriority.HIGH,
                maintenance_type="PREVENTIVE",
                suggested_within_days=7,
                rationale=narr.recommendation_rationale_health_risk(
                    asset_tag=asset_tag, asset_type=asset_type,
                    department_name=department, health_pct=health_pct,
                ),
                risk_level="HIGH",
            )

        # Warning band with failures → inspection.
        if health < 0.60 and failures >= 1:
            return MaintenanceRecommendation(
                **base,
                title=narr.recommendation_card_title_category(asset_tag, category="INSPECTION"),
                priority=RecommendationPriority.MEDIUM,
                maintenance_type="INSPECTION",
                suggested_within_days=14,
                rationale=narr.recommendation_rationale_inspection(
                    asset_tag=asset_tag, asset_type=asset_type, department_name=department,
                ),
                risk_level="MEDIUM",
            )

        # Healthy but old and heavily used → upgrade.
        if health >= 0.70 and age_days >= 400 and utilization >= 0.6:
            return MaintenanceRecommendation(
                **base,
                title=narr.recommendation_card_title_category(asset_tag, category="UPGRADE"),
                priority=RecommendationPriority.LOW,
                maintenance_type="UPGRADE",
                suggested_within_days=60,
                rationale=narr.recommendation_rationale_upgrade(
                    asset_tag=asset_tag, asset_type=asset_type, department_name=department,
                ),
                risk_level="LOW",
            )

        # Monitor band → keep monitoring (low-noise, informational).
        if 0.50 <= health < 0.70:
            return MaintenanceRecommendation(
                **base,
                title=narr.recommendation_card_title_category(asset_tag, category="MONITORING"),
                priority=RecommendationPriority.LOW,
                maintenance_type="MONITORING",
                suggested_within_days=30,
                rationale=narr.recommendation_rationale_monitoring(
                    asset_tag=asset_tag, asset_type=asset_type,
                    department_name=department, health_pct=health_pct,
                ),
                risk_level="LOW",
            )

        return None

    def list_recommendations(
        self, *, limit: int = 10, scope: AccessContext | None = None
    ) -> RecommendationListResponse:
        department_id = scope.scoping_department_id() if scope else None
        items: list[MaintenanceRecommendation] = []
        predictions = self.prediction_service.list_latest_predictions()
        allowed_ids: set[uuid.UUID] | None = None
        if department_id is not None:
            allowed_ids = self.asset_repository.filter_ids_by_department(
                [uuid.UUID(p.asset_id) for p in predictions],
                department_id,
            )

        # 1. Prediction-derived recommendations (diverse categories).
        for prediction in predictions:
            if allowed_ids is not None and uuid.UUID(prediction.asset_id) not in allowed_ids:
                continue
            rec = self._prediction_recommendation(prediction)
            if rec is not None:
                items.append(rec)

        # 2. Overdue scheduled maintenance (work already on the books).
        for record, asset in self.dashboard_repository.maintenance_due_items(
            limit=limit, department_id=department_id
        ):
            asset_type = asset.asset_type.name if asset.asset_type else None
            department_name = asset.current_department.name if asset.current_department else None
            items.append(
                MaintenanceRecommendation(
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    asset_type_name=asset_type,
                    department_name=department_name,
                    title=narr.recommendation_card_title(
                        asset.asset_tag, maintenance_type=record.maintenance_type.value
                    ),
                    priority=RecommendationPriority.HIGH,
                    maintenance_type=record.maintenance_type.value,
                    suggested_within_days=max(0, (date.today() - record.scheduled_date).days)
                    if record.scheduled_date
                    else 0,
                    rationale=narr.recommendation_rationale_overdue(
                        asset_tag=asset.asset_tag,
                        asset_type=asset_type,
                        department_name=department_name,
                        maintenance_type=record.maintenance_type.value,
                        scheduled_date=record.scheduled_date,
                    ),
                    risk_level="HIGH",
                    predicted_health_score=0.0,
                )
            )

        # 3. Warranty renewals (lifecycle, non-maintenance category).
        for asset in self.dashboard_repository.warranty_expiring_soon(
            within_days=30, limit=5, department_id=department_id
        ):
            asset_type = asset.asset_type.name if asset.asset_type else None
            department_name = asset.current_department.name if asset.current_department else None
            items.append(
                MaintenanceRecommendation(
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    asset_type_name=asset_type,
                    department_name=department_name,
                    title=narr.recommendation_card_title_category(
                        asset.asset_tag, category="WARRANTY_RENEWAL"
                    ),
                    priority=RecommendationPriority.MEDIUM,
                    maintenance_type="WARRANTY_RENEWAL",
                    suggested_within_days=max(
                        0, (asset.warranty_expiry - date.today()).days
                    )
                    if asset.warranty_expiry
                    else 0,
                    rationale=narr.recommendation_rationale_warranty(
                        asset_tag=asset.asset_tag,
                        asset_type=asset_type,
                        department_name=department_name,
                        expiry=asset.warranty_expiry,
                    ),
                    risk_level="MEDIUM",
                    predicted_health_score=0.0,
                )
            )

        # Deduplicate by asset+category, then order by priority.
        seen: set[str] = set()
        unique: list[MaintenanceRecommendation] = []
        for item in items:
            key = f"{item.asset_id}:{item.maintenance_type}"
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        unique.sort(key=lambda i: priority_order.get(i.priority.value, 3))
        return RecommendationListResponse(items=unique[:limit], total=len(unique))

    def list_for_asset(self, asset_id: uuid.UUID, *, limit: int = 5) -> RecommendationListResponse:
        all_recs = self.list_recommendations(limit=200)
        filtered = [r for r in all_recs.items if r.asset_id == str(asset_id)]
        return RecommendationListResponse(items=filtered[:limit], total=len(filtered))
