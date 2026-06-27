"""Canonical health band thresholds for fleet operations (single source of truth)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HealthBandDef:
    key: str
    label: str
    min_pct: int
    max_pct: int


HEALTH_BANDS: tuple[HealthBandDef, ...] = (
    HealthBandDef("EXCELLENT", "Excellent (90–100%)", 90, 100),
    HealthBandDef("HEALTHY", "Healthy (75–89%)", 75, 89),
    HealthBandDef("MONITOR", "Monitor (60–74%)", 60, 74),
    HealthBandDef("WARNING", "Warning (45–59%)", 45, 59),
    HealthBandDef("CRITICAL", "Critical (0–44%)", 0, 44),
)

CRITICAL_MAX_PCT = 44
WARNING_MIN_PCT = 45
WARNING_MAX_PCT = 59
MONITOR_MIN_PCT = 60
HEALTHY_MIN_PCT = 75
EXCELLENT_MIN_PCT = 90

CRITICAL_MAX_SCORE = CRITICAL_MAX_PCT / 100.0
WARNING_MIN_SCORE = WARNING_MIN_PCT / 100.0
WARNING_MAX_SCORE = WARNING_MAX_PCT / 100.0
MONITOR_MIN_SCORE = MONITOR_MIN_PCT / 100.0
HEALTHY_MIN_SCORE = HEALTHY_MIN_PCT / 100.0

# Three-tier risk bands (ML inference + fleet APIs). Subset of the five health bands above.
RISK_LOW_MIN_SCORE = 0.70
RISK_MEDIUM_MIN_SCORE = 0.50


def health_pct(score: float) -> int:
    return int(float(score) * 100)


def health_band_from_score(score: float) -> tuple[str, str]:
    pct = health_pct(score)
    if pct >= EXCELLENT_MIN_PCT:
        return "EXCELLENT", "Excellent"
    if pct >= HEALTHY_MIN_PCT:
        return "HEALTHY", "Healthy"
    if pct >= MONITOR_MIN_PCT:
        return "MONITOR", "Monitor"
    if pct >= WARNING_MIN_PCT:
        return "WARNING", "Warning"
    return "CRITICAL", "Critical"


def is_critical(score: float) -> bool:
    return health_pct(score) <= CRITICAL_MAX_PCT


def is_warning(score: float) -> bool:
    pct = health_pct(score)
    return WARNING_MIN_PCT <= pct <= WARNING_MAX_PCT


def is_monitor(score: float) -> bool:
    pct = health_pct(score)
    return MONITOR_MIN_PCT <= pct < HEALTHY_MIN_PCT


def risk_level_from_score(score: float) -> str:
    """Canonical LOW / MEDIUM / HIGH bands used by ML inference and fleet APIs."""
    if score >= RISK_LOW_MIN_SCORE:
        return "LOW"
    if score >= RISK_MEDIUM_MIN_SCORE:
        return "MEDIUM"
    return "HIGH"


def is_high_risk(score: float) -> bool:
    """True when score maps to HIGH risk (health below 50%)."""
    return risk_level_from_score(score) == "HIGH"


def is_medium_risk(score: float) -> bool:
    return risk_level_from_score(score) == "MEDIUM"


def should_notify_high_risk(score: float) -> bool:
    """Escalation notifications — same HIGH band as dashboard and assistant."""
    return is_high_risk(score)


def should_notify_drift(
    *,
    previous_health: float,
    current_health: float,
    min_drop: float = 0.10,
    severe_drop: float = 0.15,
    healthy_floor: float = 0.75,
    notify_below: float = 0.60,
) -> bool:
    """Suppress noisy drift (e.g. 89% → 79%) unless meaningful."""
    delta = current_health - previous_health
    if delta > -min_drop:
        return False
    if current_health >= healthy_floor and previous_health >= healthy_floor:
        return False
    prev_band, _ = health_band_from_score(previous_health)
    curr_band, _ = health_band_from_score(current_health)
    if prev_band == curr_band and abs(delta) < severe_drop:
        return False
    if current_health >= notify_below and abs(delta) < severe_drop:
        return False
    return True
