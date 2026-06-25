from __future__ import annotations

import uuid
from datetime import date

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.recommendation import (
    MaintenanceRecommendation,
    RecommendationListResponse,
    RecommendationPriority,
)
from app.services import narrative as narr
from app.services.prediction_service import PredictionService, get_prediction_cache


class RecommendationService:
    def __init__(
        self,
        prediction_service: PredictionService,
        dashboard_repository: DashboardRepository,
    ) -> None:
        self.prediction_service = prediction_service
        self.dashboard_repository = dashboard_repository

    def list_recommendations(self, *, limit: int = 10) -> RecommendationListResponse:
        items: list[MaintenanceRecommendation] = []

        for prediction in self.prediction_service.get_all_cached_high_risk():
            if prediction.risk_level.value == "HIGH":
                health_pct = int(prediction.health_score * 100)
                asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
                asset_tag = prediction.asset_tag or ""
                items.append(
                    MaintenanceRecommendation(
                        asset_id=prediction.asset_id,
                        asset_tag=asset_tag,
                        asset_name=asset_name,
                        title=narr.recommendation_card_title(
                            asset_name,
                            maintenance_type="PREVENTIVE",
                            urgent_health=True,
                        ),
                        priority=RecommendationPriority.HIGH,
                        maintenance_type="PREVENTIVE",
                        suggested_within_days=7,
                        rationale=narr.recommendation_rationale_health_risk(
                            asset_name=asset_name,
                            asset_tag=asset_tag,
                            health_pct=health_pct,
                        ),
                        risk_level=prediction.risk_level.value,
                        predicted_health_score=prediction.health_score,
                    )
                )

        for record, asset in self.dashboard_repository.maintenance_due_items(limit=limit):
            items.append(
                MaintenanceRecommendation(
                    asset_id=str(asset.id),
                    asset_tag=asset.asset_tag,
                    asset_name=asset.name,
                    title=narr.recommendation_card_title(
                        asset.name,
                        maintenance_type=record.maintenance_type.value,
                    ),
                    priority=RecommendationPriority.HIGH,
                    maintenance_type=record.maintenance_type.value,
                    suggested_within_days=max(0, (date.today() - record.scheduled_date).days)
                    if record.scheduled_date
                    else 0,
                    rationale=narr.recommendation_rationale_overdue(
                        asset_name=asset.name,
                        asset_tag=asset.asset_tag,
                        maintenance_type=record.maintenance_type.value,
                        scheduled_date=record.scheduled_date,
                    ),
                    risk_level="HIGH",
                    predicted_health_score=0.0,
                )
            )

        for prediction in get_prediction_cache().values():
            if prediction.risk_level.value != "MEDIUM":
                continue
            failure_count = prediction.prediction_metadata.get("failure_count", 0)
            if isinstance(failure_count, (int, float)) and failure_count >= 2:
                asset_name = prediction.asset_name or prediction.asset_tag or "Asset"
                asset_tag = prediction.asset_tag or ""
                items.append(
                    MaintenanceRecommendation(
                        asset_id=prediction.asset_id,
                        asset_tag=asset_tag,
                        asset_name=asset_name,
                        title=narr.recommendation_card_title(
                            asset_name,
                            maintenance_type="INSPECTION",
                        ),
                        priority=RecommendationPriority.MEDIUM,
                        maintenance_type="INSPECTION",
                        suggested_within_days=14,
                        rationale=narr.recommendation_rationale_inspection(
                            asset_name=asset_name,
                            asset_tag=asset_tag,
                        ),
                        risk_level="MEDIUM",
                        predicted_health_score=prediction.health_score,
                    )
                )

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
        all_recs = self.list_recommendations(limit=50)
        filtered = [r for r in all_recs.items if r.asset_id == str(asset_id)]
        return RecommendationListResponse(items=filtered[:limit], total=len(filtered))
