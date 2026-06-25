from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ml.config import DEFAULT_TRAINING_RAW
from ml.data.synthetic_generator import generate_dataset, write_generation_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic AI training dataset")
    parser.add_argument("--rows", type=int, default=80_000)
    parser.add_argument("--assets", type=int, default=9_000)
    parser.add_argument("--history-months", type=int, default=24)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=DEFAULT_TRAINING_RAW)
    args = parser.parse_args(argv)

    print(
        f"Generating {args.rows} snapshots across {args.assets} assets "
        f"({args.history_months} months, seed={args.seed})..."
    )
    df = generate_dataset(
        rows=args.rows,
        assets=args.assets,
        history_months=args.history_months,
        seed=args.seed,
        output=args.output,
    )
    report = write_generation_report(df, seed=args.seed, history_months=args.history_months)
    print(f"Wrote {args.output} ({len(df)} rows, {report['unique_assets']} assets)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
