from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class SeedProfile:
    name: str
    departments: int
    employees: int
    active_assets: int
    inactive_assets: int
    history_months: int
    allocation_events: int
    transfer_events: int
    maintenance_records: int
    health_snapshots: int
    random_seed: int


MINIMAL = SeedProfile(
    name="minimal",
    departments=4,
    employees=20,
    active_assets=30,
    inactive_assets=5,
    history_months=1,
    allocation_events=40,
    transfer_events=10,
    maintenance_records=25,
    health_snapshots=80,
    random_seed=42,
)

DEMO = SeedProfile(
    name="demo",
    departments=10,
    employees=90,
    active_assets=200,
    inactive_assets=20,
    history_months=18,
    allocation_events=300,
    transfer_events=75,
    maintenance_records=150,
    health_snapshots=1500,
    random_seed=42,
)

ML = SeedProfile(
    name="ml",
    departments=10,
    employees=90,
    active_assets=200,
    inactive_assets=20,
    history_months=18,
    allocation_events=300,
    transfer_events=75,
    maintenance_records=150,
    health_snapshots=2400,
    random_seed=42,
)

ENTERPRISE = SeedProfile(
    name="enterprise",
    departments=10,
    employees=175,
    active_assets=400,
    inactive_assets=40,
    history_months=24,
    allocation_events=728,
    transfer_events=180,
    maintenance_records=550,
    health_snapshots=3500,
    random_seed=42,
)

PROFILES: dict[str, SeedProfile] = {
    "minimal": MINIMAL,
    "demo": DEMO,
    "ml": ML,
    "enterprise": ENTERPRISE,
}


def history_start(*, months: int, end: date | None = None) -> date:
    end = end or date.today()
    return end - timedelta(days=months * 30)
