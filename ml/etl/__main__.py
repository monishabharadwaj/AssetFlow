from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ml.config import DEFAULT_TRAINING_DATASET, DEFAULT_TRAINING_RAW, DEFAULT_VALIDATION_DATASET
from ml.etl.dataset import build_training_dataset
from ml.etl.sources.database_source import DatabaseSource
from ml.etl.sources.parquet_source import ParquetSource


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AssetFlow AI ETL pipeline")
    parser.add_argument("--source", choices=["file", "db"], default="file")
    parser.add_argument("--input", type=Path, default=DEFAULT_TRAINING_RAW)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    if args.source == "file":
        source = ParquetSource(args.input)
        output = args.output or DEFAULT_TRAINING_DATASET
    else:
        source = DatabaseSource()
        output = args.output or DEFAULT_VALIDATION_DATASET

    print(f"Extracting from {args.source}...")
    raw_df = source.extract()
    print(f"Extracted {len(raw_df)} rows")

    if args.source == "file":
        result = build_training_dataset(raw_df, output=output, seed=args.seed)
        print(f"Wrote training dataset: {output} ({len(result)} rows)")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        raw_df.to_parquet(output, index=False)
        print(f"Wrote validation extract: {output} ({len(raw_df)} rows)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
