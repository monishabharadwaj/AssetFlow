from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


OPERATIONAL_TABLES = (
    "asset_health_history",
    "maintenance_records",
    "asset_transfers",
    "asset_allocations",
    "assets",
    "employees",
    "departments",
)


def reset_operational_data(db: Session) -> None:
    """Remove operational rows; preserve schema and lookup categories/types."""
    for table in OPERATIONAL_TABLES:
        db.execute(text(f"DELETE FROM {table}"))
    db.commit()
