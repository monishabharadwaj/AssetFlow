import uuid

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_asset_service
from app.schemas.asset import AssetCategoryResponse, AssetTypeResponse
from app.services.asset_service import AssetService

router = APIRouter()


@router.get("/asset-categories", response_model=list[AssetCategoryResponse])
def list_asset_categories(
    service: AssetService = Depends(get_asset_service),
) -> list[AssetCategoryResponse]:
    return service.list_categories()


@router.get("/asset-types", response_model=list[AssetTypeResponse])
def list_asset_types(
    category_id: uuid.UUID | None = Query(default=None),
    service: AssetService = Depends(get_asset_service),
) -> list[AssetTypeResponse]:
    return service.list_asset_types(category_id=category_id)
