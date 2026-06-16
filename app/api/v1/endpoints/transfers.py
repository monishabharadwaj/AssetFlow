import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_transfer_service
from app.schemas.transfer import TransferCreate, TransferListResponse, TransferResponse
from app.services.transfer_service import TransferService

router = APIRouter()


@router.post(
    "/assets/{asset_id}/transfers",
    response_model=TransferResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transfer(
    asset_id: uuid.UUID,
    data: TransferCreate,
    service: TransferService = Depends(get_transfer_service),
) -> TransferResponse:
    return service.create(asset_id, data)


@router.get("/assets/{asset_id}/transfers", response_model=TransferListResponse)
def list_asset_transfers(
    asset_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: TransferService = Depends(get_transfer_service),
) -> TransferListResponse:
    return service.list_by_asset(asset_id, page=page, page_size=page_size)
