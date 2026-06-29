import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.auth_deps import get_access_context
from app.api.deps import get_asset_service
from app.core.access_scope import AccessContext
from app.core.enums import AssetStatus
from app.schemas.asset import (
    AssetCreate,
    AssetListResponse,
    AssetResponse,
    AssetUpdate,
)
from app.services.asset_service import AssetService

router = APIRouter()


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(
    data: AssetCreate,
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    return service.create(data, scope)


@router.get("/search", response_model=AssetListResponse)
def search_assets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    name: str | None = Query(default=None),
    asset_tag: str | None = Query(default=None),
    serial_number: str | None = Query(default=None),
    current_status: AssetStatus | None = Query(default=None),
    current_department_id: uuid.UUID | None = Query(default=None),
    current_location: str | None = Query(default=None),
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetListResponse:
    return service.search(
        page=page,
        page_size=page_size,
        name=name,
        asset_tag=asset_tag,
        serial_number=serial_number,
        current_status=current_status,
        current_department_id=current_department_id,
        current_location=current_location,
        scope=scope,
    )


@router.get("", response_model=AssetListResponse)
def list_assets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    is_active: bool | None = Query(default=None),
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetListResponse:
    return service.list(page=page, page_size=page_size, is_active=is_active, scope=scope)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: uuid.UUID,
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    return service.get_by_id(asset_id, scope)


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: uuid.UUID,
    data: AssetUpdate,
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    return service.update(asset_id, data, scope)


@router.delete("/{asset_id}", response_model=AssetResponse)
def deactivate_asset(
    asset_id: uuid.UUID,
    scope: AccessContext = Depends(get_access_context),
    service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    return service.deactivate(asset_id, scope)
