from __future__ import annotations

from dataclasses import dataclass

from app.seeding.manifest import ASSET_TYPE_SPECS


@dataclass(frozen=True)
class TypeProfile:
    expected_life_days: int
    max_operational_hours: float
    baseline_downtime_hours: float
    util_min: float
    util_max: float
    downtime_sensitivity: float
    maintenance_effect: float


_DEFAULT = TypeProfile(
    expected_life_days=1825,
    max_operational_hours=8000.0,
    baseline_downtime_hours=24.0,
    util_min=0.2,
    util_max=0.75,
    downtime_sensitivity=1.0,
    maintenance_effect=0.08,
)

_TYPE_OVERRIDES: dict[str, TypeProfile] = {
    "Laptop": TypeProfile(1460, 6000, 12, 0.25, 0.85, 0.8, 0.10),
    "Desktop Workstation": TypeProfile(1825, 7000, 16, 0.20, 0.70, 0.7, 0.09),
    "Server": TypeProfile(2555, 20000, 48, 0.40, 0.95, 1.4, 0.07),
    "Networking Device": TypeProfile(2190, 15000, 36, 0.35, 0.90, 1.2, 0.07),
    "Monitor": TypeProfile(2190, 5000, 8, 0.15, 0.55, 0.5, 0.06),
    "Printer": TypeProfile(1460, 4000, 20, 0.20, 0.65, 0.9, 0.08),
    "Office Furniture": TypeProfile(3650, 2000, 4, 0.05, 0.30, 0.3, 0.04),
    "Conference AV": TypeProfile(1825, 3000, 14, 0.10, 0.50, 0.6, 0.06),
    "UPS": TypeProfile(1825, 12000, 28, 0.30, 0.80, 1.1, 0.07),
    "Company Vehicle": TypeProfile(2555, 12000, 72, 0.35, 0.90, 1.5, 0.09),
    "Delivery Van": TypeProfile(2190, 14000, 80, 0.40, 0.95, 1.6, 0.09),
    "Production Machine": TypeProfile(3285, 25000, 96, 0.45, 0.98, 1.8, 0.08),
}


def get_type_profile(asset_type: str) -> TypeProfile:
    return _TYPE_OVERRIDES.get(asset_type, _DEFAULT)


def asset_type_weights() -> dict[str, float]:
    return {name: spec[0] for name, spec in ASSET_TYPE_SPECS.items()}
