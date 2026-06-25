from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from ml.config import DEFAULT_FEATURE_STATS, DEFAULT_MODEL_PATH
from ml.data.schema import FEATURE_COLUMNS
from ml.etl.sources.database_source import DatabaseSource
from ml.predict import predict_from_features


class FeatureEngineeringService:
    def extract_asset_features(self, asset_id: uuid.UUID) -> dict:
        import pandas as pd
        from sqlalchemy import select

        from app.core.database import SessionLocal
        from app.models.asset import Asset

        db = SessionLocal()
        try:
            source = DatabaseSource(db)
            df = source.extract()
            if df.empty:
                raise ValueError("No health history available for feature extraction")

            asset_id_str = str(asset_id)
            asset_rows = df[df["synthetic_asset_id"] == asset_id_str]
            if asset_rows.empty:
                asset = db.execute(select(Asset).where(Asset.id == asset_id)).scalar_one_or_none()
                if asset is None:
                    raise ValueError("Asset not found")
                return self._default_features_for_asset(asset, db)

            latest = asset_rows.iloc[-1]
            return {col: latest[col] for col in FEATURE_COLUMNS if col in latest}
        finally:
            db.close()

    def _default_features_for_asset(self, asset, db) -> dict:
        from sqlalchemy import func, select

        from app.models.asset import AssetType
        from app.models.maintenance import MaintenanceRecord
        from ml.data.type_profiles import get_type_profile
        from ml.etl.features import derive_utilization_rate

        type_name = db.execute(
            select(AssetType.name).where(AssetType.id == asset.asset_type_id)
        ).scalar_one_or_none() or "Laptop"

        today = date.today()
        age_days = max(0, (today - asset.purchase_date).days)
        profile = get_type_profile(type_name)

        maintenance_count = db.execute(
            select(func.count())
            .select_from(MaintenanceRecord)
            .where(MaintenanceRecord.asset_id == asset.id)
        ).scalar_one()

        last_maint = db.execute(
            select(func.max(MaintenanceRecord.scheduled_date))
            .where(MaintenanceRecord.asset_id == asset.id)
        ).scalar_one()
        days_since_maint = (today - last_maint).days if last_maint else age_days

        operational_hours = min(
            profile.max_operational_hours,
            age_days * (profile.max_operational_hours / 365) * 0.4,
        )

        return {
            "asset_type": type_name,
            "asset_age_days": age_days,
            "utilization_rate": derive_utilization_rate(operational_hours, type_name),
            "operational_hours": operational_hours,
            "maintenance_count": int(maintenance_count),
            "days_since_last_maintenance": int(days_since_maint),
            "failure_count": 0,
            "downtime_hours": profile.baseline_downtime_hours,
            "allocation_count": 0,
            "transfer_count": 0,
        }
