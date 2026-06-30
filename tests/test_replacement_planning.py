"""Unit tests for replacement planning rationale and divergence helpers."""
from __future__ import annotations

from app.schemas.operations import ReplacementPlanItem
from app.services.replacement_planning_service import (
    build_replacement_rationale,
    count_life_health_divergence,
    life_health_divergence_score,
)


def test_divergence_rationale_lead() -> None:
    text = build_replacement_rationale(
        asset_name="IT Office Furniture #0005",
        type_name="Office Furniture",
        age_days=478,
        expected_life_days=3650,
        health_score=0.09,
        life_remaining_pct=87.0,
        priority="HIGH",
        features={"failure_count": 2, "days_since_last_maintenance": 180},
    )
    assert "Operational degradation despite remaining calendar life" in text
    assert "87%" in text or "87.0%" in text
    assert "9%" in text
    assert "2 recorded failures" in text
    assert "Escalate to capital planning this quarter" in text
    assert "Plan budget for replacement before reliability drops further" not in text


def test_end_of_life_rationale() -> None:
    text = build_replacement_rationale(
        asset_name="Old Server",
        type_name="Server",
        age_days=2400,
        expected_life_days=2555,
        health_score=0.55,
        life_remaining_pct=6.0,
        priority="MEDIUM",
    )
    assert "Approaching end of expected useful life" in text
    assert "Include in next budget cycle" in text


def test_priority_closings_differ() -> None:
    high = build_replacement_rationale(
        asset_name="A",
        type_name="Laptop",
        age_days=100,
        expected_life_days=1460,
        health_score=0.3,
        life_remaining_pct=90,
        priority="HIGH",
    )
    medium = build_replacement_rationale(
        asset_name="B",
        type_name="Laptop",
        age_days=100,
        expected_life_days=1460,
        health_score=0.3,
        life_remaining_pct=90,
        priority="MEDIUM",
    )
    low = build_replacement_rationale(
        asset_name="C",
        type_name="Laptop",
        age_days=100,
        expected_life_days=1460,
        health_score=0.3,
        life_remaining_pct=90,
        priority="LOW",
    )
    assert high != medium != low
    assert "Escalate to capital planning" in high
    assert "Include in next budget cycle" in medium
    assert "Monitor quarterly" in low


def test_life_health_divergence_score() -> None:
    assert life_health_divergence_score(life_remaining_pct=87, health_score=0.09) > 0.7
    assert life_health_divergence_score(life_remaining_pct=20, health_score=0.8) == 0.0


def test_count_life_health_divergence() -> None:
    items = [
        ReplacementPlanItem(
            asset_id="1",
            asset_tag="A-1",
            asset_name="A",
            asset_type="Laptop",
            health_score=0.09,
            age_days=100,
            life_remaining_pct=87,
            replace_within_months=3,
            rationale="",
            priority="HIGH",
        ),
        ReplacementPlanItem(
            asset_id="2",
            asset_tag="B-1",
            asset_name="B",
            asset_type="Laptop",
            health_score=0.8,
            age_days=100,
            life_remaining_pct=87,
            replace_within_months=12,
            rationale="",
            priority="LOW",
        ),
    ]
    assert count_life_health_divergence(items) == 1
