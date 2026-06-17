import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_timeline_service
from app.schemas.timeline import AssetTimelineResponse
from app.services.timeline_service import TimelineService

router = APIRouter()


@router.get("/assets/{asset_id}/timeline", response_model=AssetTimelineResponse)
def get_asset_timeline(
    asset_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: TimelineService = Depends(get_timeline_service),
) -> AssetTimelineResponse:
    return service.get_asset_timeline(asset_id, page=page, page_size=page_size)
