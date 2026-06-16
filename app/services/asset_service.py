from __future__ import annotations

import uuid

from app.core.enums import AssetStatus
from app.exceptions.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset import (
    AssetCategoryResponse,
    AssetCreate,
    AssetResponse,
    AssetTypeResponse,
    AssetUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.department_service import DepartmentService


class AssetService:
    def __init__(
        self,
        repository: AssetRepository,
        department_service: DepartmentService,
    ) -> None:
        self.repository = repository
        self.department_service = department_service

    def create(self, data: AssetCreate) -> AssetResponse:
        self.department_service.get_active_department(data.current_department_id)

        if not self.repository.get_asset_type(data.asset_type_id):
            raise NotFoundError("AssetType", str(data.asset_type_id))

        if self.repository.get_by_tag(data.asset_tag):
            raise ConflictError(f"Asset with tag '{data.asset_tag}' already exists")

        asset = Asset(
            asset_tag=data.asset_tag,
            name=data.name,
            asset_type_id=data.asset_type_id,
            purchase_date=data.purchase_date,
            purchase_cost=data.purchase_cost,
            current_status=AssetStatus.AVAILABLE,
            current_location=data.current_location,
            current_department_id=data.current_department_id,
            current_assigned_employee_id=None,
            serial_number=data.serial_number,
            manufacturer=data.manufacturer,
            model=data.model,
            warranty_expiry=data.warranty_expiry,
            is_active=True,
        )
        self.repository.create(asset)
        self.repository.commit()
        self.repository.refresh(asset)
        return AssetResponse.model_validate(asset)

    def get_by_id(self, asset_id: uuid.UUID) -> AssetResponse:
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise NotFoundError("Asset", str(asset_id))
        return AssetResponse.model_validate(asset)

    def get_active_asset(self, asset_id: uuid.UUID) -> Asset:
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise NotFoundError("Asset", str(asset_id))
        if not asset.is_active:
            raise BusinessRuleError("Asset is inactive")
        return asset

    def list(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
    ) -> PaginatedResponse[AssetResponse]:
        items, total = self.repository.list(page=page, page_size=page_size, is_active=is_active)
        return PaginatedResponse.create(
            items=[AssetResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def search(
        self,
        *,
        page: int,
        page_size: int,
        name: str | None = None,
        asset_tag: str | None = None,
        serial_number: str | None = None,
        current_status: AssetStatus | None = None,
        current_department_id: uuid.UUID | None = None,
        current_location: str | None = None,
    ) -> PaginatedResponse[AssetResponse]:
        items, total = self.repository.search(
            page=page,
            page_size=page_size,
            name=name,
            asset_tag=asset_tag,
            serial_number=serial_number,
            current_status=current_status,
            current_department_id=current_department_id,
            current_location=current_location,
        )
        return PaginatedResponse.create(
            items=[AssetResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, asset_id: uuid.UUID, data: AssetUpdate) -> AssetResponse:
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise NotFoundError("Asset", str(asset_id))

        update_data = data.model_dump(exclude_unset=True)

        if "current_department_id" in update_data:
            self.department_service.get_active_department(update_data["current_department_id"])

        if "asset_type_id" in update_data:
            if not self.repository.get_asset_type(update_data["asset_type_id"]):
                raise NotFoundError("AssetType", str(update_data["asset_type_id"]))

        if "asset_tag" in update_data:
            existing = self.repository.get_by_tag(update_data["asset_tag"])
            if existing and existing.id != asset_id:
                raise ConflictError(f"Asset with tag '{update_data['asset_tag']}' already exists")

        self.repository.update(asset, update_data)
        self.repository.commit()
        self.repository.refresh(asset)
        return AssetResponse.model_validate(asset)

    def deactivate(self, asset_id: uuid.UUID) -> AssetResponse:
        asset = self.repository.get_by_id(asset_id)
        if not asset:
            raise NotFoundError("Asset", str(asset_id))

        if not asset.is_active:
            return AssetResponse.model_validate(asset)

        if asset.current_status == AssetStatus.ASSIGNED:
            raise BusinessRuleError("Cannot deactivate an asset that is currently assigned")

        asset.is_active = False
        self.repository.commit()
        self.repository.refresh(asset)
        return AssetResponse.model_validate(asset)

    def list_categories(self) -> list[AssetCategoryResponse]:
        categories = self.repository.list_categories()
        return [AssetCategoryResponse.model_validate(c) for c in categories]

    def list_asset_types(self, category_id: uuid.UUID | None = None) -> list[AssetTypeResponse]:
        types = self.repository.list_asset_types(category_id=category_id)
        return [AssetTypeResponse.model_validate(t) for t in types]

    def update_asset_state(
        self,
        asset: Asset,
        *,
        status: AssetStatus | None = None,
        assigned_employee_id: uuid.UUID | None = ...,  # type: ignore[assignment]
        department_id: uuid.UUID | None = None,
        location: str | None = None,
    ) -> Asset:
        if status is not None:
            asset.current_status = status
        if assigned_employee_id is not ...:
            asset.current_assigned_employee_id = assigned_employee_id
        if department_id is not None:
            asset.current_department_id = department_id
        if location is not None:
            asset.current_location = location
        self.repository.flush()
        return asset
