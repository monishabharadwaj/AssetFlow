from __future__ import annotations

import uuid

from app.core.enums import AllocationAction, AssetStatus
from app.exceptions.errors import BusinessRuleError
from app.models.allocation import AssetAllocation
from app.repositories.allocation_repository import AllocationRepository
from app.schemas.allocation import (
    AllocationAssignRequest,
    AllocationListResponse,
    AllocationReassignRequest,
    AllocationResponse,
    AllocationReturnRequest,
)
from app.schemas.common import PaginatedResponse
from app.services.asset_service import AssetService
from app.services.employee_service import EmployeeService


class AllocationService:
    def __init__(
        self,
        repository: AllocationRepository,
        asset_service: AssetService,
        employee_service: EmployeeService,
    ) -> None:
        self.repository = repository
        self.asset_service = asset_service
        self.employee_service = employee_service

    def assign(self, asset_id: uuid.UUID, data: AllocationAssignRequest) -> AllocationResponse:
        asset = self.asset_service.get_active_asset(asset_id)
        if asset.current_status != AssetStatus.AVAILABLE:
            raise BusinessRuleError("Asset must be AVAILABLE to assign")

        self.employee_service.get_active_employee(data.employee_id)

        allocation = AssetAllocation(
            asset_id=asset_id,
            employee_id=data.employee_id,
            action=AllocationAction.ASSIGN,
            allocated_at=data.allocated_at,
            notes=data.notes,
            performed_by=data.performed_by,
        )
        self.repository.create(allocation)
        self.asset_service.update_asset_state(
            asset,
            status=AssetStatus.ASSIGNED,
            assigned_employee_id=data.employee_id,
        )
        self.repository.commit()
        self.repository.refresh(allocation)
        return AllocationResponse.model_validate(allocation)

    def return_asset(self, asset_id: uuid.UUID, data: AllocationReturnRequest) -> AllocationResponse:
        asset = self.asset_service.get_active_asset(asset_id)
        if asset.current_status != AssetStatus.ASSIGNED:
            raise BusinessRuleError("Asset must be ASSIGNED to return")

        open_allocation = self.repository.get_open_allocation(asset_id)
        if not open_allocation:
            raise BusinessRuleError("No open allocation found for this asset")

        allocation = AssetAllocation(
            asset_id=asset_id,
            employee_id=open_allocation.employee_id,
            action=AllocationAction.RETURN,
            allocated_at=open_allocation.allocated_at,
            returned_at=data.returned_at,
            notes=data.notes,
            performed_by=data.performed_by,
        )
        self.repository.create(allocation)

        if open_allocation.returned_at is None:
            open_allocation.returned_at = data.returned_at

        self.asset_service.update_asset_state(
            asset,
            status=AssetStatus.AVAILABLE,
            assigned_employee_id=None,
        )
        self.repository.commit()
        self.repository.refresh(allocation)
        return AllocationResponse.model_validate(allocation)

    def reassign(self, asset_id: uuid.UUID, data: AllocationReassignRequest) -> AllocationResponse:
        asset = self.asset_service.get_active_asset(asset_id)
        if asset.current_status != AssetStatus.ASSIGNED:
            raise BusinessRuleError("Asset must be ASSIGNED to reassign")

        if asset.current_assigned_employee_id == data.employee_id:
            raise BusinessRuleError("Asset is already assigned to this employee")

        self.employee_service.get_active_employee(data.employee_id)

        open_allocation = self.repository.get_open_allocation(asset_id)
        if open_allocation and open_allocation.returned_at is None:
            open_allocation.returned_at = data.allocated_at

        allocation = AssetAllocation(
            asset_id=asset_id,
            employee_id=data.employee_id,
            action=AllocationAction.REASSIGN,
            allocated_at=data.allocated_at,
            notes=data.notes,
            performed_by=data.performed_by,
        )
        self.repository.create(allocation)
        self.asset_service.update_asset_state(
            asset,
            status=AssetStatus.ASSIGNED,
            assigned_employee_id=data.employee_id,
        )
        self.repository.commit()
        self.repository.refresh(allocation)
        return AllocationResponse.model_validate(allocation)

    def list_by_asset(
        self,
        asset_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[AllocationResponse]:
        self.asset_service.get_by_id(asset_id)
        items, total = self.repository.list_by_asset(asset_id, page=page, page_size=page_size)
        return PaginatedResponse.create(
            items=[AllocationResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def list_by_employee(
        self,
        employee_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
    ) -> PaginatedResponse[AllocationResponse]:
        self.employee_service.get_by_id(employee_id)
        items, total = self.repository.list_by_employee(
            employee_id, page=page, page_size=page_size
        )
        return PaginatedResponse.create(
            items=[AllocationResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
