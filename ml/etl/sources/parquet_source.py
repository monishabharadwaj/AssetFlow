from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.data.schema import ALL_COLUMNS, FEATURE_COLUMNS, LABEL_COLUMN, METADATA_COLUMNS


class ParquetSource:
    def __init__(self, path: Path) -> None:
        self.path = path

    def extract(self) -> pd.DataFrame:
        df = pd.read_parquet(self.path)
        missing = set(FEATURE_COLUMNS + [LABEL_COLUMN]) - set(df.columns)
        if missing:
            raise ValueError(f"Parquet missing columns: {missing}")
        cols = [c for c in ALL_COLUMNS if c in df.columns]
        return df[cols].copy()
