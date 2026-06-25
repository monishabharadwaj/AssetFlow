from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ml.data.schema import FEATURE_COLUMNS, LABEL_COLUMN, NUMERIC_FEATURE_COLUMNS
from ml.data.type_profiles import get_type_profile


def derive_utilization_rate(operational_hours: float, asset_type: str) -> float:
    profile = get_type_profile(asset_type)
    if profile.max_operational_hours <= 0:
        return 0.0
    return min(1.0, max(0.0, operational_hours / profile.max_operational_hours))


def fit_feature_stats(df: pd.DataFrame) -> dict[str, Any]:
    stats: dict[str, Any] = {
        "numeric": {},
        "asset_type_categories": sorted(df["asset_type"].astype(str).unique().tolist()),
    }
    for col in NUMERIC_FEATURE_COLUMNS:
        series = df[col].astype(float)
        stats["numeric"][col] = {
            "mean": float(series.mean()),
            "std": float(series.std()) or 1.0,
            "min": float(series.min()),
            "max": float(series.max()),
        }
    return stats


def normalize_features(df: pd.DataFrame, stats: dict[str, Any]) -> pd.DataFrame:
    out = df.copy()
    for col in NUMERIC_FEATURE_COLUMNS:
        if col not in stats["numeric"]:
            continue
        s = stats["numeric"][col]
        out[f"{col}_norm"] = (out[col].astype(float) - s["mean"]) / s["std"]
    type_to_idx = {t: i for i, t in enumerate(stats["asset_type_categories"])}
    out["asset_type_idx"] = out["asset_type"].map(type_to_idx).fillna(0).astype(int)
    return out


def save_feature_stats(stats: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def load_feature_stats(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def vectorize_row(row: dict[str, Any], stats: dict[str, Any]) -> tuple[np.ndarray, int]:
    """Return (numeric_features[10], asset_type_idx) for inference."""
    asset_type = str(row.get("asset_type", "Laptop"))
    type_to_idx = {t: i for i, t in enumerate(stats["asset_type_categories"])}
    type_idx = type_to_idx.get(asset_type, 0)

    numeric_values: list[float] = []
    for col in NUMERIC_FEATURE_COLUMNS:
        raw = float(row.get(col, 0))
        s = stats["numeric"].get(col, {"mean": 0.0, "std": 1.0})
        numeric_values.append((raw - s["mean"]) / s["std"])

    return np.array(numeric_values, dtype=np.float32), type_idx
