from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.models.health_history import AssetHealthHistory
from app.repositories.health_history_repository import HealthHistoryRepository
from app.schemas.common import PaginatedResponse
from app.schemas.health_history import (
    HealthHistoryCreate,
    HealthHistoryListResponse,
    HealthHistoryResponse,
)
from app.services.asset_service import AssetService


class HealthHistoryService:
    def __init__(
        self,
        repository: HealthHistoryRepository,
        asset_service: AssetService,
    ) -> None:
        self.repository = repository
        self.asset_service = asset_service

    def create(self, asset_id: uuid.UUID, data: HealthHistoryCreate) -> HealthHistoryResponse:
        self.asset_service.get_active_asset(asset_id)

        recorded_at = data.recorded_at or datetime.now(timezone.utc)
        record = AssetHealthHistory(
            asset_id=asset_id,
            recorded_at=recorded_at,
            health_score=data.health_score,
            condition_rating=data.condition_rating,
            operational_hours=data.operational_hours,
            failure_count=data.failure_count,
            days_since_last_maintenance=data.days_since_last_maintenance,
            age_in_days=data.age_in_days,
            depreciation_ratio=data.depreciation_ratio,
            raw_features=data.raw_features,
            prediction_metadata=data.prediction_metadata,
            notes=data.notes,
        )
        self.repository.create(record)
        self.repository.commit()
        self.repository.refresh(record)
        return HealthHistoryResponse.model_validate(record)

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[HealthHistoryResponse]:
        self.asset_service.get_by_id(asset_id)
        items, total = self.repository.list_by_asset(asset_id, page=page, page_size=page_size)
        return PaginatedResponse.create(
            items=[HealthHistoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
