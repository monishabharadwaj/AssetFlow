from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select

from app.core.config import settings
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.schemas.health_history import HealthHistoryCreate
from app.schemas.intelligence import (
    BatchScoreResponse,
    HealthPredictionResponse,
    HighRiskAssetItem,
    HighRiskListResponse,
    RiskLevel,
)
from app.services.asset_service import AssetService
from app.services.feature_engineering import FeatureEngineeringService
from app.services.health_history_service import HealthHistoryService
from ml.config import DATASET_NAME
from ml.predict import predict_from_features

_PREDICTION_CACHE: dict[str, HealthPredictionResponse] = {}


def get_prediction_cache() -> dict[str, HealthPredictionResponse]:
    return _PREDICTION_CACHE


class PredictionService:
    def __init__(
        self,
        asset_service: AssetService,
        feature_service: FeatureEngineeringService,
        health_service: HealthHistoryService | None = None,
        asset_repository: AssetRepository | None = None,
    ) -> None:
        self.asset_service = asset_service
        self.feature_service = feature_service
        self.health_service = health_service
        self.asset_repository = asset_repository

    def _model_paths(self) -> tuple[Path, Path]:
        return Path(settings.ml_model_path), Path(settings.ml_feature_stats_path)

    def predict_asset(
        self,
        asset_id: uuid.UUID,
        *,
        persist: bool = False,
    ) -> HealthPredictionResponse:
        if not settings.ml_enabled:
            raise RuntimeError("ML predictions are disabled")

        asset = self.asset_service.get_by_id(asset_id)
        features = self.feature_service.extract_asset_features(asset_id)
        model_path, stats_path = self._model_paths()

        raw = predict_from_features(features, model_path=model_path, stats_path=stats_path)
        predicted_at = datetime.now(timezone.utc)

        metadata = {
            "model_version": raw["model_version"],
            "predicted_at": predicted_at.isoformat(),
            "risk_level": raw["risk_level"],
            "confidence": raw["confidence"],
            "features_used": raw["features_used"],
            "training_dataset": raw.get("training_dataset", DATASET_NAME),
        }

        if persist and self.health_service:
            self.health_service.create(
                asset_id,
                HealthHistoryCreate(
                    health_score=Decimal(str(raw["health_score"])),
                    operational_hours=Decimal(str(features.get("operational_hours", 0))),
                    failure_count=int(features.get("failure_count", 0)),
                    days_since_last_maintenance=int(features.get("days_since_last_maintenance", 0)),
                    age_in_days=int(features.get("asset_age_days", 0)),
                    prediction_metadata=metadata,
                    notes="AI health assessment",
                ),
            )

        response = HealthPredictionResponse(
            asset_id=str(asset.id),
            asset_tag=asset.asset_tag,
            asset_name=asset.name,
            health_score=float(raw["health_score"]),
            risk_level=RiskLevel(raw["risk_level"]),
            confidence=float(raw["confidence"]),
            model_version=raw["model_version"],
            training_dataset=raw.get("training_dataset", DATASET_NAME),
            features_used=raw["features_used"],
            prediction_metadata=metadata,
            predicted_at=predicted_at,
        )
        _PREDICTION_CACHE[str(asset.id)] = response
        return response

    def score_batch(self, *, persist: bool = False) -> BatchScoreResponse:
        if not self.asset_repository:
            raise RuntimeError("Asset repository required for batch scoring")

        results: list[HealthPredictionResponse] = []
        failed = 0
        page = 1
        while True:
            assets, total = self.asset_repository.list(page=page, page_size=200, is_active=True)
            if not assets:
                break
            for asset in assets:
                try:
                    results.append(self.predict_asset(asset.id, persist=persist))
                except Exception:
                    failed += 1
            if page * 200 >= total:
                break
            page += 1

        return BatchScoreResponse(scored=len(results), failed=failed, results=results)

    def is_cache_warm(self) -> bool:
        return bool(_PREDICTION_CACHE)

    def get_high_risk(self, *, limit: int = 20) -> HighRiskListResponse:
        items = [
            HighRiskAssetItem(
                asset_id=p.asset_id,
                asset_tag=p.asset_tag or "",
                asset_name=p.asset_name or "",
                health_score=p.health_score,
                risk_level=p.risk_level,
                predicted_at=p.predicted_at,
            )
            for p in _PREDICTION_CACHE.values()
            if p.risk_level == RiskLevel.HIGH
        ]
        items.sort(key=lambda i: i.health_score)
        return HighRiskListResponse(items=items[:limit], total=len(items))

    def get_cached_prediction(self, asset_id: uuid.UUID) -> HealthPredictionResponse | None:
        return _PREDICTION_CACHE.get(str(asset_id))

    def get_all_cached_high_risk(self) -> list[HealthPredictionResponse]:
        return [p for p in _PREDICTION_CACHE.values() if p.risk_level == RiskLevel.HIGH]
