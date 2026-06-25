from __future__ import annotations

from pathlib import Path

ML_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ML_ROOT / "artifacts"

DATASET_NAME = "synthetic_v1_80k"

DEFAULT_TRAINING_RAW = ARTIFACTS_DIR / "training_raw.parquet"
DEFAULT_TRAINING_DATASET = ARTIFACTS_DIR / "training_dataset.parquet"
DEFAULT_VALIDATION_DATASET = ARTIFACTS_DIR / "validation_dataset.parquet"
DEFAULT_FEATURE_STATS = ARTIFACTS_DIR / "feature_stats.json"
DEFAULT_DATASET_MANIFEST = ARTIFACTS_DIR / "dataset_manifest.json"
DEFAULT_MODEL_PATH = ARTIFACTS_DIR / "model.pt"
DEFAULT_TRAINING_REPORT = ARTIFACTS_DIR / "training_report.json"
DEFAULT_GENERATION_REPORT = ARTIFACTS_DIR / "generation_report.json"

# Risk thresholds (shared across training, inference, UI)
RISK_LOW_MIN = 0.70
RISK_MEDIUM_MIN = 0.50
