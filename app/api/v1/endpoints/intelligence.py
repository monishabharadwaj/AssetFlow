import uuid

from fastapi import APIRouter, Depends, Query

from app.api.auth_deps import get_access_context
from app.api.deps import (
    get_prediction_service,
    get_recommendation_service,
    get_root_cause_service,
)
from app.core.access_scope import AccessContext
from app.schemas.explanation import RootCauseResponse
from app.schemas.intelligence import (
    BatchScoreResponse,
    HealthPredictionResponse,
    HighRiskListResponse,
)
from app.schemas.recommendation import RecommendationListResponse
from app.services.prediction_service import PredictionService, get_prediction_cache
from app.services.recommendation_service import RecommendationService
from app.services.root_cause_service import RootCauseService


router = APIRouter()


@router.post(
    "/intelligence/assets/{asset_id}/predict",
    response_model=HealthPredictionResponse,
)
def predict_asset_health(
    asset_id: uuid.UUID,
    persist: bool = Query(default=False),
    service: PredictionService = Depends(get_prediction_service),
) -> HealthPredictionResponse:
    return service.predict_asset(asset_id, persist=persist)


@router.post("/intelligence/score-batch", response_model=BatchScoreResponse)
def score_batch(
    persist: bool = Query(default=False),
    service: PredictionService = Depends(get_prediction_service),
) -> BatchScoreResponse:
    return service.score_batch(persist=persist)


@router.get("/intelligence/high-risk", response_model=HighRiskListResponse)
def list_high_risk_assets(
    limit: int = Query(default=20, ge=1, le=100),
    service: PredictionService = Depends(get_prediction_service),
) -> HighRiskListResponse:
    return service.get_high_risk(limit=limit)


@router.get("/intelligence/cache-status")
def prediction_cache_status(
    service: PredictionService = Depends(get_prediction_service),
) -> dict[str, bool | int]:
    cache = get_prediction_cache()
    return {"warm": service.is_cache_warm(), "scored_assets": len(cache)}


@router.get("/intelligence/recommendations", response_model=RecommendationListResponse)
def list_recommendations(
    limit: int = Query(default=10, ge=1, le=50),
    scope: AccessContext = Depends(get_access_context),
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationListResponse:
    return service.list_recommendations(limit=limit, scope=scope)


@router.get(
    "/intelligence/assets/{asset_id}/recommendations",
    response_model=RecommendationListResponse,
)
def list_asset_recommendations(
    asset_id: uuid.UUID,
    limit: int = Query(default=5, ge=1, le=20),
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendationListResponse:
    return service.list_for_asset(asset_id, limit=limit)


@router.get(
    "/intelligence/assets/{asset_id}/root-cause",
    response_model=RootCauseResponse,
)
async def get_asset_root_cause(
    asset_id: uuid.UUID,
    use_llm: bool = Query(default=True),
    service: RootCauseService = Depends(get_root_cause_service),
) -> RootCauseResponse:
    return await service.get_root_cause(asset_id, use_llm=use_llm)

