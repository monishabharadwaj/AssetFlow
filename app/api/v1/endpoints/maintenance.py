import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.auth_deps import get_access_context
from app.api.deps import get_maintenance_service
from app.core.access_scope import AccessContext
from app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceListResponse,
    MaintenanceResponse,
    MaintenanceUpdate,
    MaintenanceWorkQueueResponse,
)
from app.services.maintenance_service import MaintenanceService

router = APIRouter()


@router.get("/maintenance", response_model=MaintenanceWorkQueueResponse)
def list_maintenance_work_queue(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceWorkQueueResponse:
    return service.list_work_queue(page=page, page_size=page_size, scope=scope)


@router.post(
    "/assets/{asset_id}/maintenance",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_maintenance_record(
    asset_id: uuid.UUID,
    data: MaintenanceCreate,
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceResponse:
    return service.create(asset_id, data, scope)


@router.get("/assets/{asset_id}/maintenance", response_model=MaintenanceListResponse)
def list_asset_maintenance(
    asset_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceListResponse:
    return service.list_by_asset(asset_id, page=page, page_size=page_size, scope=scope)


@router.get("/maintenance/{record_id}", response_model=MaintenanceResponse)
def get_maintenance_record(
    record_id: uuid.UUID,
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceResponse:
    return service.get_by_id(record_id, scope)


@router.patch("/maintenance/{record_id}", response_model=MaintenanceResponse)
def update_maintenance_record(
    record_id: uuid.UUID,
    data: MaintenanceUpdate,
    scope: AccessContext = Depends(get_access_context),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceResponse:
    return service.update(record_id, data, scope)
