import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.auth_deps import get_access_context
from app.api.deps import get_allocation_service
from app.core.access_scope import AccessContext
from app.schemas.allocation import (
    AllocationAssignRequest,
    AllocationListResponse,
    AllocationReassignRequest,
    AllocationResponse,
    AllocationReturnRequest,
)
from app.services.allocation_service import AllocationService

router = APIRouter()


@router.post(
    "/assets/{asset_id}/allocations/assign",
    response_model=AllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_asset(
    asset_id: uuid.UUID,
    data: AllocationAssignRequest,
    scope: AccessContext = Depends(get_access_context),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationResponse:
    return service.assign(asset_id, data, scope)


@router.post(
    "/assets/{asset_id}/allocations/return",
    response_model=AllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def return_asset(
    asset_id: uuid.UUID,
    data: AllocationReturnRequest,
    scope: AccessContext = Depends(get_access_context),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationResponse:
    return service.return_asset(asset_id, data, scope)


@router.post(
    "/assets/{asset_id}/allocations/reassign",
    response_model=AllocationResponse,
    status_code=status.HTTP_201_CREATED,
)
def reassign_asset(
    asset_id: uuid.UUID,
    data: AllocationReassignRequest,
    scope: AccessContext = Depends(get_access_context),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationResponse:
    return service.reassign(asset_id, data, scope)


@router.get("/assets/{asset_id}/allocations", response_model=AllocationListResponse)
def list_asset_allocations(
    asset_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    scope: AccessContext = Depends(get_access_context),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationListResponse:
    return service.list_by_asset(asset_id, page=page, page_size=page_size, scope=scope)


@router.get("/employees/{employee_id}/allocations", response_model=AllocationListResponse)
def list_employee_allocations(
    employee_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    scope: AccessContext = Depends(get_access_context),
    service: AllocationService = Depends(get_allocation_service),
) -> AllocationListResponse:
    return service.list_by_employee(employee_id, page=page, page_size=page_size, scope=scope)
