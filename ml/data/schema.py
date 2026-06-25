from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ml.config import DATASET_NAME

FEATURE_COLUMNS: list[str] = [
    "asset_type",
    "asset_age_days",
    "utilization_rate",
    "operational_hours",
    "maintenance_count",
    "days_since_last_maintenance",
    "failure_count",
    "downtime_hours",
    "allocation_count",
    "transfer_count",
]

LABEL_COLUMN = "health_score"

METADATA_COLUMNS: list[str] = [
    "synthetic_asset_id",
    "snapshot_date",
    "risk_level",
    "dataset_name",
]

ALL_COLUMNS: list[str] = FEATURE_COLUMNS + [LABEL_COLUMN] + METADATA_COLUMNS

NUMERIC_FEATURE_COLUMNS: list[str] = [c for c in FEATURE_COLUMNS if c != "asset_type"]


@dataclass(frozen=True)
class TrainingRow:
    asset_type: str
    asset_age_days: int
    utilization_rate: float
    operational_hours: float
    maintenance_count: int
    days_since_last_maintenance: int
    failure_count: int
    downtime_hours: float
    allocation_count: int
    transfer_count: int
    health_score: float
    synthetic_asset_id: str
    snapshot_date: str
    risk_level: str
    dataset_name: str = DATASET_NAME

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_type": self.asset_type,
            "asset_age_days": self.asset_age_days,
            "utilization_rate": self.utilization_rate,
            "operational_hours": self.operational_hours,
            "maintenance_count": self.maintenance_count,
            "days_since_last_maintenance": self.days_since_last_maintenance,
            "failure_count": self.failure_count,
            "downtime_hours": self.downtime_hours,
            "allocation_count": self.allocation_count,
            "transfer_count": self.transfer_count,
            "health_score": self.health_score,
            "synthetic_asset_id": self.synthetic_asset_id,
            "snapshot_date": self.snapshot_date,
            "risk_level": self.risk_level,
            "dataset_name": self.dataset_name,
        }


def risk_level_from_score(score: float) -> str:
    if score >= 0.70:
        return "LOW"
    if score >= 0.50:
        return "MEDIUM"
    return "HIGH"
