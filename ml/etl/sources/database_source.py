from __future__ import annotations

import math
from datetime import date, datetime, timezone

import pandas as pd
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.allocation import AssetAllocation
from app.models.asset import Asset, AssetType
from app.models.health_history import AssetHealthHistory
from app.models.maintenance import MaintenanceRecord
from app.models.transfer import AssetTransfer
from ml.config import DATASET_NAME
from ml.data.schema import FEATURE_COLUMNS, LABEL_COLUMN, METADATA_COLUMNS, risk_level_from_score
from ml.data.type_profiles import get_type_profile
from ml.etl.features import derive_utilization_rate


class DatabaseSource:
    def __init__(self, db: Session | None = None) -> None:
        self._db = db
        self._owns_session = db is None

    def extract(self) -> pd.DataFrame:
        db = self._db or SessionLocal()
        try:
            return self._extract(db)
        finally:
            if self._owns_session:
                db.close()

    def _extract(self, db: Session) -> pd.DataFrame:
        type_map = {
            str(t.id): t.name
            for t in db.execute(select(AssetType)).scalars().all()
        }
        health_rows = db.execute(
            select(AssetHealthHistory, Asset)
            .join(Asset, Asset.id == AssetHealthHistory.asset_id)
            .where(Asset.is_active.is_(True))
        ).all()

        records: list[dict] = []
        today = date.today()

        for health, asset in health_rows:
            asset_type = type_map.get(str(asset.asset_type_id), "Laptop")
            snapshot_date = health.recorded_at.date() if health.recorded_at else today
            age_days = health.age_in_days or max(0, (snapshot_date - asset.purchase_date).days)

            maintenance_count = db.execute(
                select(func.count())
                .select_from(MaintenanceRecord)
                .where(
                    MaintenanceRecord.asset_id == asset.id,
                    MaintenanceRecord.scheduled_date <= snapshot_date,
                )
            ).scalar_one()

            last_maint = db.execute(
                select(func.max(MaintenanceRecord.scheduled_date))
                .where(
                    MaintenanceRecord.asset_id == asset.id,
                    MaintenanceRecord.scheduled_date <= snapshot_date,
                )
            ).scalar_one()
            days_since_maint = (
                (snapshot_date - last_maint).days if last_maint else age_days
            )

            allocation_count = db.execute(
                select(func.count())
                .select_from(AssetAllocation)
                .where(
                    AssetAllocation.asset_id == asset.id,
                    AssetAllocation.allocated_at <= datetime.combine(
                        snapshot_date, datetime.min.time(), tzinfo=timezone.utc
                    ),
                )
            ).scalar_one()

            transfer_count = db.execute(
                select(func.count())
                .select_from(AssetTransfer)
                .where(
                    AssetTransfer.asset_id == asset.id,
                    AssetTransfer.transferred_at <= datetime.combine(
                        snapshot_date, datetime.min.time(), tzinfo=timezone.utc
                    ),
                )
            ).scalar_one()

            operational_hours = float(health.operational_hours or 0)
            profile = get_type_profile(asset_type)
            if operational_hours <= 0:
                operational_hours = min(
                    profile.max_operational_hours,
                    age_days * (profile.max_operational_hours / 365) * 0.4,
                )
            utilization_rate = derive_utilization_rate(operational_hours, asset_type)

            failure_count = health.failure_count
            downtime_hours = profile.baseline_downtime_hours * profile.downtime_sensitivity
            downtime_hours += failure_count * 8.0 * profile.downtime_sensitivity

            health_score = float(health.health_score) if health.health_score is not None else None
            if health_score is None:
                continue

            records.append(
                {
                    "asset_type": asset_type,
                    "asset_age_days": age_days,
                    "utilization_rate": utilization_rate,
                    "operational_hours": operational_hours,
                    "maintenance_count": int(maintenance_count),
                    "days_since_last_maintenance": int(days_since_maint),
                    "failure_count": int(failure_count),
                    "downtime_hours": round(downtime_hours, 2),
                    "allocation_count": int(allocation_count),
                    "transfer_count": int(transfer_count),
                    LABEL_COLUMN: health_score,
                    "synthetic_asset_id": str(asset.id),
                    "snapshot_date": snapshot_date.isoformat(),
                    "risk_level": risk_level_from_score(health_score),
                    "dataset_name": DATASET_NAME,
                }
            )

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame(columns=FEATURE_COLUMNS + [LABEL_COLUMN] + METADATA_COLUMNS)
        return df
