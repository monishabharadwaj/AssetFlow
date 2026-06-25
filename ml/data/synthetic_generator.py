"""
Lifecycle-aware synthetic enterprise health snapshot generator.

Causal health formula (per snapshot):
  maintenance_bonus = maint_effect * log1p(maintenance_count) * exp(-days_since_last_maintenance / 90)
  base_health = 1.0
    - age_factor     * (asset_age_days / expected_life_days[type])
    - util_factor    * utilization_rate
    - hours_factor   * (operational_hours / max_hours[type])
    - neglect_factor * log1p(days_since_last_maintenance / 60)
    - failure_factor * failure_count
    - downtime_factor* (downtime_hours / type_baseline_downtime[type])
    - mobility_factor* log1p(allocation_count + transfer_count) * 0.02
    + maintenance_bonus
    + gaussian_noise(σ=0.025)
  health_score = clip(base_health, 0.05, 0.99)
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from ml.config import DATASET_NAME, DEFAULT_GENERATION_REPORT, DEFAULT_TRAINING_RAW
from ml.data.schema import TrainingRow, risk_level_from_score
from ml.data.type_profiles import asset_type_weights, get_type_profile


@dataclass
class LifecycleState:
    asset_type: str
    purchase_date: date
    maintenance_dates: list[date] = field(default_factory=list)
    failure_dates: list[date] = field(default_factory=list)
    allocation_dates: list[date] = field(default_factory=list)
    transfer_dates: list[date] = field(default_factory=list)
    cumulative_operational_hours: float = 0.0


def _weighted_asset_type(rng: random.Random) -> str:
    weights = asset_type_weights()
    types = list(weights.keys())
    probs = [weights[t] for t in types]
    total = sum(probs)
    probs = [p / total for p in probs]
    return rng.choices(types, weights=probs, k=1)[0]


def _simulate_lifecycle(
    rng: random.Random,
    asset_type: str,
    purchase_date: date,
    history_end: date,
) -> LifecycleState:
    state = LifecycleState(asset_type=asset_type, purchase_date=purchase_date)
    profile = get_type_profile(asset_type)
    days_span = max(1, (history_end - purchase_date).days)

    # Maintenance events (more for high-touch types)
    maint_rate = 0.08 if asset_type in ("Server", "Company Vehicle", "Delivery Van", "Production Machine") else 0.05
    n_maint = max(1, int(days_span / 90 * maint_rate * rng.uniform(0.7, 1.3)))
    for _ in range(n_maint):
        day_offset = rng.randint(30, days_span)
        state.maintenance_dates.append(purchase_date + timedelta(days=day_offset))
    state.maintenance_dates.sort()

    # Failures correlate with age
    failure_prob = 0.03 if asset_type in ("Laptop", "Printer") else 0.02
    n_failures = rng.randint(0, max(1, int(days_span / 365 * failure_prob * 3)))
    for _ in range(n_failures):
        day_offset = rng.randint(60, days_span)
        state.failure_dates.append(purchase_date + timedelta(days=day_offset))
    state.failure_dates.sort()

    # Allocations / transfers for assignable types
    if asset_type in ("Laptop", "Desktop Workstation", "Company Vehicle", "Delivery Van"):
        n_alloc = rng.randint(1, 5)
        for _ in range(n_alloc):
            day_offset = rng.randint(0, days_span)
            state.allocation_dates.append(purchase_date + timedelta(days=day_offset))
        n_transfer = rng.randint(0, 3)
        for _ in range(n_transfer):
            day_offset = rng.randint(0, days_span)
            state.transfer_dates.append(purchase_date + timedelta(days=day_offset))

    # Cumulative hours grow with utilization
    util = rng.uniform(profile.util_min, profile.util_max)
    hours_per_day = (profile.max_operational_hours / 365) * util
    state.cumulative_operational_hours = min(
        profile.max_operational_hours,
        hours_per_day * days_span * rng.uniform(0.8, 1.1),
    )
    return state


def _features_at_snapshot(
    rng: random.Random,
    state: LifecycleState,
    snapshot_date: date,
) -> dict[str, Any]:
    profile = get_type_profile(state.asset_type)
    age_days = max(0, (snapshot_date - state.purchase_date).days)

    maintenance_count = sum(1 for d in state.maintenance_dates if d <= snapshot_date)
    last_maint = max((d for d in state.maintenance_dates if d <= snapshot_date), default=None)
    days_since_maint = (snapshot_date - last_maint).days if last_maint else age_days

    failure_count = sum(1 for d in state.failure_dates if d <= snapshot_date)
    allocation_count = sum(1 for d in state.allocation_dates if d <= snapshot_date)
    transfer_count = sum(1 for d in state.transfer_dates if d <= snapshot_date)

    progress = min(1.0, age_days / max(1, (snapshot_date - state.purchase_date).days + 1))
    operational_hours = min(
        profile.max_operational_hours,
        state.cumulative_operational_hours * progress * rng.uniform(0.95, 1.05),
    )
    utilization_rate = min(1.0, operational_hours / profile.max_operational_hours)

    downtime_hours = profile.baseline_downtime_hours * profile.downtime_sensitivity
    downtime_hours += failure_count * rng.uniform(4, 24) * profile.downtime_sensitivity
    downtime_hours += max(0, days_since_maint - 120) * 0.05

    return {
        "asset_type": state.asset_type,
        "asset_age_days": age_days,
        "utilization_rate": round(utilization_rate, 4),
        "operational_hours": round(operational_hours, 2),
        "maintenance_count": maintenance_count,
        "days_since_last_maintenance": days_since_maint,
        "failure_count": failure_count,
        "downtime_hours": round(downtime_hours, 2),
        "allocation_count": allocation_count,
        "transfer_count": transfer_count,
    }


def _compute_health_score(rng: random.Random, features: dict[str, Any]) -> float:
    asset_type = features["asset_type"]
    profile = get_type_profile(asset_type)

    maint_bonus = profile.maintenance_effect * math.log1p(features["maintenance_count"]) * math.exp(
        -features["days_since_last_maintenance"] / 90
    )

    base = 1.0
    base -= 0.35 * (features["asset_age_days"] / profile.expected_life_days)
    base -= 0.15 * features["utilization_rate"]
    base -= 0.10 * (features["operational_hours"] / profile.max_operational_hours)
    base -= 0.12 * math.log1p(features["days_since_last_maintenance"] / 60)
    base -= 0.08 * features["failure_count"]
    base -= 0.10 * (features["downtime_hours"] / max(profile.baseline_downtime_hours, 1))
    base -= 0.02 * math.log1p(features["allocation_count"] + features["transfer_count"])
    base += maint_bonus
    base += rng.gauss(0, 0.025)

    return max(0.05, min(0.99, base))


def _snapshot_dates_for_asset(
    rng: random.Random,
    purchase_date: date,
    history_end: date,
    n_snapshots: int,
    maintenance_dates: list[date],
) -> list[date]:
    dates: set[date] = set()
    span = max(1, (history_end - purchase_date).days)

    # Regular progression points
    for i in range(n_snapshots):
        offset = int(span * (i + 1) / (n_snapshots + 1))
        dates.add(purchase_date + timedelta(days=max(0, offset)))

    # Cluster after maintenance
    for md in maintenance_dates:
        if purchase_date <= md <= history_end:
            dates.add(md)
            post = md + timedelta(days=rng.randint(7, 30))
            if post <= history_end:
                dates.add(post)

    # Ensure at least n_snapshots
    while len(dates) < n_snapshots:
        dates.add(purchase_date + timedelta(days=rng.randint(0, span)))

    result = sorted(dates)[: max(n_snapshots, len(dates))]
    return result[:n_snapshots] if len(result) > n_snapshots else result


def generate_dataset(
    *,
    rows: int = 80_000,
    assets: int = 9_000,
    history_months: int = 24,
    seed: int = 42,
    output: Path | None = None,
) -> pd.DataFrame:
    rng = random.Random(seed)
    history_end = date.today()
    history_start = history_end - timedelta(days=history_months * 30)

    snapshots_per_asset = max(1, rows // assets)
    extra = rows - snapshots_per_asset * assets

    all_rows: list[dict[str, Any]] = []

    for asset_idx in range(assets):
        asset_id = f"SYN-{asset_idx:05d}"
        asset_type = _weighted_asset_type(rng)
        profile = get_type_profile(asset_type)

        max_purchase_offset = history_months * 30 - 60
        purchase_offset = rng.randint(0, max(0, max_purchase_offset))
        purchase_date = history_start + timedelta(days=purchase_offset)

        state = _simulate_lifecycle(rng, asset_type, purchase_date, history_end)
        n_snaps = snapshots_per_asset + (1 if asset_idx < extra else 0)
        snap_dates = _snapshot_dates_for_asset(
            rng, purchase_date, history_end, n_snaps, state.maintenance_dates
        )

        for snap_date in snap_dates:
            features = _features_at_snapshot(rng, state, snap_date)
            health = _compute_health_score(rng, features)
            row = TrainingRow(
                asset_type=features["asset_type"],
                asset_age_days=features["asset_age_days"],
                utilization_rate=features["utilization_rate"],
                operational_hours=features["operational_hours"],
                maintenance_count=features["maintenance_count"],
                days_since_last_maintenance=features["days_since_last_maintenance"],
                failure_count=features["failure_count"],
                downtime_hours=features["downtime_hours"],
                allocation_count=features["allocation_count"],
                transfer_count=features["transfer_count"],
                health_score=round(health, 4),
                synthetic_asset_id=asset_id,
                snapshot_date=snap_date.isoformat(),
                risk_level=risk_level_from_score(health),
            )
            all_rows.append(row.to_dict())

    df = pd.DataFrame(all_rows)
    out = output or DEFAULT_TRAINING_RAW
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    return df


def write_generation_report(
    df: pd.DataFrame,
    *,
    seed: int,
    history_months: int,
    output: Path | None = None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "dataset_name": DATASET_NAME,
        "seed": seed,
        "history_months": history_months,
        "row_count": len(df),
        "unique_assets": int(df["synthetic_asset_id"].nunique()),
        "date_range": {
            "min": str(df["snapshot_date"].min()),
            "max": str(df["snapshot_date"].max()),
        },
        "health_score": {
            "mean": float(df["health_score"].mean()),
            "std": float(df["health_score"].std()),
            "min": float(df["health_score"].min()),
            "max": float(df["health_score"].max()),
        },
        "risk_level_distribution": df["risk_level"].value_counts().to_dict(),
        "asset_type_distribution": df["asset_type"].value_counts().to_dict(),
    }
    path = output or DEFAULT_GENERATION_REPORT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
