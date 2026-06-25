from __future__ import annotations

import argparse
import sys

from app.core.database import SessionLocal
from app.seeding.generator import run_seed
from app.seeding.profiles import PROFILES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed AssetFlow AI demo data")
    parser.add_argument(
        "--profile",
        choices=list(PROFILES.keys()),
        default="demo",
        help="Seed profile (default: demo)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear operational data before seeding",
    )
    args = parser.parse_args(argv)

    profile = PROFILES[args.profile]
    db = SessionLocal()
    try:
        counts = run_seed(db, profile, reset=args.reset)
        print(f"Seed complete — profile: {profile.name}")
        for key, value in counts.items():
            if key != "profile":
                print(f"  {key}: {value}")
    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
