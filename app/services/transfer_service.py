from __future__ import annotations

import uuid

from app.core.enums import AssetStatus
from app.exceptions.errors import BusinessRuleError
from app.models.transfer import AssetTransfer
from app.repositories.transfer_repository import TransferRepository
from app.schemas.common import PaginatedResponse
from app.schemas.transfer import TransferCreate, TransferListResponse, TransferResponse
from app.services.asset_service import AssetService
from app.services.department_service import DepartmentService


class TransferService:
    def __init__(
        self,
        repository: TransferRepository,
        asset_service: AssetService,
        department_service: DepartmentService,
    ) -> None:
        self.repository = repository
        self.asset_service = asset_service
        self.department_service = department_service

    def create(self, asset_id: uuid.UUID, data: TransferCreate) -> TransferResponse:
        asset = self.asset_service.get_active_asset(asset_id)

        if asset.current_status in (AssetStatus.RETIRED, AssetStatus.DISPOSED):
            raise BusinessRuleError("Cannot transfer a retired or disposed asset")

        self.department_service.get_active_department(data.to_department_id)

        if (
            asset.current_department_id == data.to_department_id
            and asset.current_location == data.to_location
        ):
            raise BusinessRuleError(
                "Transfer must change department or location"
            )

        transfer = AssetTransfer(
            asset_id=asset_id,
            from_department_id=asset.current_department_id,
            to_department_id=data.to_department_id,
            from_location=asset.current_location,
            to_location=data.to_location,
            transferred_at=data.transferred_at,
            reason=data.reason,
            performed_by=data.performed_by,
        )
        self.repository.create(transfer)
        self.asset_service.update_asset_state(
            asset,
            department_id=data.to_department_id,
            location=data.to_location,
        )
        self.repository.commit()
        self.repository.refresh(transfer)
        return TransferResponse.model_validate(transfer)

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[TransferResponse]:
        self.asset_service.get_by_id(asset_id)
        items, total = self.repository.list_by_asset(asset_id, page=page, page_size=page_size)
        return PaginatedResponse.create(
            items=[TransferResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
