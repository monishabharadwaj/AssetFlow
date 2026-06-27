from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from app.core.config import settings
from app.core.health_thresholds import is_high_risk, risk_level_from_score
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

    @staticmethod
    def _history_to_response(
        *,
        asset_id: uuid.UUID,
        asset_tag: str | None,
        asset_name: str | None,
        asset_type_name: str | None,
        department_name: str | None,
        health_score: float,
        meta: dict,
        recorded_at: datetime,
    ) -> HealthPredictionResponse:
        risk = risk_level_from_score(health_score)
        return HealthPredictionResponse(
            asset_id=str(asset_id),
            asset_tag=asset_tag,
            asset_name=asset_name,
            asset_type_name=asset_type_name,
            department_name=department_name,
            health_score=health_score,
            risk_level=RiskLevel(risk),
            confidence=float(meta.get("confidence", 1.0)),
            model_version=meta.get("model_version", "unknown"),
            training_dataset=meta.get("training_dataset", "unknown"),
            features_used=meta.get("features_used", []),
            prediction_metadata=meta,
            predicted_at=recorded_at,
        )

    def predict_asset(
        self,
        asset_id: uuid.UUID,
        *,
        persist: bool = True,
    ) -> HealthPredictionResponse:
        if not settings.ml_enabled:
            raise RuntimeError("ML predictions are disabled")

        asset = self.asset_service.get_by_id(asset_id)
        features = self.feature_service.extract_asset_features(asset_id)
        model_path, stats_path = self._model_paths()

        raw = predict_from_features(features, model_path=model_path, stats_path=stats_path)
        predicted_at = datetime.now(timezone.utc)
        fleet_ctx = (
            self.asset_repository.get_fleet_context_for_assets([asset_id])
            if self.asset_repository
            else {}
        )
        context = fleet_ctx.get(asset_id, {})
        asset_type_name = context.get("asset_type_name")
        department_name = context.get("department_name")

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
            asset_type_name=asset_type_name,
            department_name=department_name,
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

    def score_batch(self, *, persist: bool = True) -> BatchScoreResponse:
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

    def ensure_predictions_loaded(self) -> None:
        if not _PREDICTION_CACHE:
            self._load_cache_from_db()

    def is_cache_warm(self) -> bool:
        self.ensure_predictions_loaded()
        return bool(_PREDICTION_CACHE)

    def list_latest_predictions(self) -> list[HealthPredictionResponse]:
        self.ensure_predictions_loaded()
        return list(_PREDICTION_CACHE.values())

    def get_high_risk(self, *, limit: int = 20) -> HighRiskListResponse:
        self.ensure_predictions_loaded()
        items = [
            HighRiskAssetItem(
                asset_id=p.asset_id,
                asset_tag=p.asset_tag or "",
                asset_name=p.asset_name or "",
                asset_type_name=p.asset_type_name,
                department_name=p.department_name,
                health_score=p.health_score,
                risk_level=p.risk_level,
                predicted_at=p.predicted_at,
            )
            for p in _PREDICTION_CACHE.values()
            if is_high_risk(p.health_score)
        ]
        items.sort(key=lambda i: i.health_score)
        return HighRiskListResponse(items=items[:limit], total=len(items))

    def get_cached_prediction(self, asset_id: uuid.UUID) -> HealthPredictionResponse | None:
        cached = _PREDICTION_CACHE.get(str(asset_id))
        if cached is not None:
            return cached
        if self.health_service and self.health_service.repository:
            history = self.health_service.repository.get_latest_prediction_for_asset(asset_id)
            if history:
                health_score = float(history.health_score) if history.health_score is not None else 0.0
                meta = history.prediction_metadata or {}
                response = self._history_to_response(
                    asset_id=history.asset_id,
                    asset_tag=history.asset.asset_tag if history.asset else None,
                    asset_name=history.asset.name if history.asset else None,
                    asset_type_name=(
                        history.asset.asset_type.name
                        if history.asset and history.asset.asset_type
                        else None
                    ),
                    department_name=(
                        history.asset.current_department.name
                        if history.asset and history.asset.current_department
                        else None
                    ),
                    health_score=health_score,
                    meta=meta,
                    recorded_at=history.recorded_at,
                )
                _PREDICTION_CACHE[str(asset_id)] = response
                return response
        return None

    def get_all_cached_high_risk(self) -> list[HealthPredictionResponse]:
        self.ensure_predictions_loaded()
        return [p for p in _PREDICTION_CACHE.values() if is_high_risk(p.health_score)]

    def _load_cache_from_db(self) -> None:
        if not self.asset_repository or not self.health_service:
            return

        assets_map: dict[uuid.UUID, object] = {}
        page = 1
        while True:
            assets, total = self.asset_repository.list(page=page, page_size=200, is_active=True)
            if not assets:
                break
            for asset in assets:
                assets_map[asset.id] = asset
            if page * 200 >= total:
                break
            page += 1

        histories = self.health_service.repository.get_latest_ai_predictions_per_asset()
        fleet_context = self.asset_repository.get_fleet_context_for_assets(
            [history.asset_id for history in histories]
        )
        for history in histories:
            asset = assets_map.get(history.asset_id)
            if not asset:
                continue
            context = fleet_context.get(history.asset_id, {})
            health_score = float(history.health_score) if history.health_score is not None else 0.0
            meta = history.prediction_metadata or {}
            response = self._history_to_response(
                asset_id=history.asset_id,
                asset_tag=context.get("asset_tag") or asset.asset_tag,
                asset_name=asset.name,
                asset_type_name=context.get("asset_type_name"),
                department_name=context.get("department_name"),
                health_score=health_score,
                meta=meta,
                recorded_at=history.recorded_at,
            )
            _PREDICTION_CACHE[str(asset.id)] = response
