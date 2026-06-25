from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ml.config import DATASET_NAME, DEFAULT_DATASET_MANIFEST, DEFAULT_FEATURE_STATS, DEFAULT_TRAINING_DATASET
from ml.data.schema import FEATURE_COLUMNS, LABEL_COLUMN, METADATA_COLUMNS
from ml.etl.features import fit_feature_stats, normalize_features, save_feature_stats


def asset_id_column(df: pd.DataFrame) -> str:
    if "synthetic_asset_id" in df.columns:
        return "synthetic_asset_id"
    return "synthetic_asset_id"


def split_by_asset(
    df: pd.DataFrame,
    *,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    id_col = asset_id_column(df)
    asset_ids = df[id_col].unique()
    rng = pd.Series(asset_ids).sample(frac=1, random_state=seed).tolist()

    n = len(rng)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    train_ids = set(rng[:n_train])
    val_ids = set(rng[n_train : n_train + n_val])
    test_ids = set(rng[n_train + n_val :])

    train_df = df[df[id_col].isin(train_ids)].copy()
    val_df = df[df[id_col].isin(val_ids)].copy()
    test_df = df[df[id_col].isin(test_ids)].copy()
    return train_df, val_df, test_df


def build_training_dataset(
    raw_df: pd.DataFrame,
    *,
    output: Path | None = None,
    stats_path: Path | None = None,
    manifest_path: Path | None = None,
    seed: int = 42,
) -> pd.DataFrame:
    train_df, val_df, test_df = split_by_asset(raw_df, seed=seed)
    stats = fit_feature_stats(train_df)

    train_norm = normalize_features(train_df, stats)
    val_norm = normalize_features(val_df, stats)
    test_norm = normalize_features(test_df, stats)

    train_norm["split"] = "train"
    val_norm["split"] = "val"
    test_norm["split"] = "test"

    combined = pd.concat([train_norm, val_norm, test_norm], ignore_index=True)

    out = output or DEFAULT_TRAINING_DATASET
    stats_out = stats_path or DEFAULT_FEATURE_STATS
    manifest_out = manifest_path or DEFAULT_DATASET_MANIFEST

    out.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out, index=False)
    save_feature_stats(stats, stats_out)

    manifest: dict[str, Any] = {
        "dataset_name": DATASET_NAME,
        "total_rows": len(combined),
        "train_rows": len(train_norm),
        "val_rows": len(val_norm),
        "test_rows": len(test_norm),
        "train_assets": int(train_df[asset_id_column(train_df)].nunique()),
        "val_assets": int(val_df[asset_id_column(val_df)].nunique()),
        "test_assets": int(test_df[asset_id_column(test_df)].nunique()),
        "feature_columns": FEATURE_COLUMNS,
        "label_column": LABEL_COLUMN,
        "metadata_columns": METADATA_COLUMNS,
        "seed": seed,
    }
    manifest_out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return combined
