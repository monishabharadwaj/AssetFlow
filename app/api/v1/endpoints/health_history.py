import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_health_history_service
from app.schemas.health_history import (
    HealthHistoryCreate,
    HealthHistoryListResponse,
    HealthHistoryResponse,
)
from app.services.health_history_service import HealthHistoryService

router = APIRouter()


@router.post(
    "/assets/{asset_id}/health-history",
    response_model=HealthHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_health_snapshot(
    asset_id: uuid.UUID,
    data: HealthHistoryCreate,
    service: HealthHistoryService = Depends(get_health_history_service),
) -> HealthHistoryResponse:
    return service.create(asset_id, data)


@router.get("/assets/{asset_id}/health-history", response_model=HealthHistoryListResponse)
def list_health_history(
    asset_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: HealthHistoryService = Depends(get_health_history_service),
) -> HealthHistoryListResponse:
    return service.list_by_asset(asset_id, page=page, page_size=page_size)
