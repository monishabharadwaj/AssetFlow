from __future__ import annotations

import uuid

from app.core.enums import AssetStatus, MaintenanceStatus
from app.exceptions.errors import NotFoundError
from app.models.maintenance import MaintenanceRecord
from app.repositories.maintenance_repository import MaintenanceRepository
from app.schemas.common import PaginatedResponse
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceListResponse,
    MaintenanceResponse,
    MaintenanceUpdate,
)
from app.services.asset_service import AssetService


class MaintenanceService:
    def __init__(
        self,
        repository: MaintenanceRepository,
        asset_service: AssetService,
    ) -> None:
        self.repository = repository
        self.asset_service = asset_service

    def create(self, asset_id: uuid.UUID, data: MaintenanceCreate) -> MaintenanceResponse:
        self.asset_service.get_active_asset(asset_id)

        record = MaintenanceRecord(
            asset_id=asset_id,
            maintenance_type=data.maintenance_type,
            status=data.status,
            scheduled_date=data.scheduled_date,
            completed_date=data.completed_date,
            cost=data.cost,
            description=data.description,
            service_provider=data.service_provider,
            performed_by=data.performed_by,
        )
        self.repository.create(record)

        if data.status == MaintenanceStatus.IN_PROGRESS:
            asset = self.asset_service.get_active_asset(asset_id)
            self.asset_service.update_asset_state(asset, status=AssetStatus.IN_MAINTENANCE)

        self.repository.commit()
        self.repository.refresh(record)
        return MaintenanceResponse.model_validate(record)

    def get_by_id(self, record_id: uuid.UUID) -> MaintenanceResponse:
        record = self.repository.get_by_id(record_id)
        if not record:
            raise NotFoundError("MaintenanceRecord", str(record_id))
        return MaintenanceResponse.model_validate(record)

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[MaintenanceResponse]:
        self.asset_service.get_by_id(asset_id)
        items, total = self.repository.list_by_asset(asset_id, page=page, page_size=page_size)
        return PaginatedResponse.create(
            items=[MaintenanceResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, record_id: uuid.UUID, data: MaintenanceUpdate) -> MaintenanceResponse:
        record = self.repository.get_by_id(record_id)
        if not record:
            raise NotFoundError("MaintenanceRecord", str(record_id))

        old_status = record.status
        update_data = data.model_dump(exclude_unset=True)
        self.repository.update(record, update_data)

        new_status = update_data.get("status", old_status)
        if new_status != old_status:
            self._apply_status_side_effects(record.asset_id, new_status)

        self.repository.commit()
        self.repository.refresh(record)
        return MaintenanceResponse.model_validate(record)

    def _apply_status_side_effects(
        self,
        asset_id: uuid.UUID,
        status: MaintenanceStatus,
    ) -> None:
        asset = self.asset_service.get_active_asset(asset_id)

        if status == MaintenanceStatus.IN_PROGRESS:
            self.asset_service.update_asset_state(asset, status=AssetStatus.IN_MAINTENANCE)
        elif status in (MaintenanceStatus.COMPLETED, MaintenanceStatus.CANCELLED):
            restored_status = (
                AssetStatus.ASSIGNED
                if asset.current_assigned_employee_id
                else AssetStatus.AVAILABLE
            )
            self.asset_service.update_asset_state(asset, status=restored_status)
