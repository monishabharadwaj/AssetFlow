"""Unit tests for assistant intent scoring and fuzzy routing."""
from __future__ import annotations

import pytest

from app.services.assistant_routing import (
    SCORE_THRESHOLD,
    heuristic_tool,
    score_message,
)


@pytest.mark.parametrize(
    ("message", "expected_tool"),
    [
        ("which assets are at high risk", "get_high_risk_assets"),
        ("show me critical fleet units", "get_high_risk_assets"),
        ("any assets in danger?", "get_high_risk_assets"),
        ("list unhealthy assets", "get_high_risk_assets"),
        ("what maintenance is overdue", "get_overdue_maintenance"),
        ("maintenance past due", "get_overdue_maintenance"),
        ("how many assets do we have", "get_fleet_counts"),
        ("give me a fleet overview", "get_dashboard_summary"),
        ("fleet summary please", "get_dashboard_summary"),
        ("which assets need attention", "get_high_risk_assets"),
        ("show risky laptops", "get_high_risk_by_type"),
        ("any unhealthy laptops?", "get_high_risk_by_type"),
        ("what's the worst health in the fleet", "get_worst_health_assets"),
        ("assets currently in maintenance", "get_assets_in_maintenance"),
    ],
)
def test_score_message_top_tool(message: str, expected_tool: str) -> None:
    ranked = score_message(message)
    assert ranked, f"No scores for: {message}"
    assert ranked[0][0] == expected_tool, f"{message!r} -> {ranked[:3]}"
    assert ranked[0][1] >= SCORE_THRESHOLD


def test_heuristic_risk_plus_asset() -> None:
    assert heuristic_tool("tell me about risky fleet items") == "get_high_risk_assets"


def test_heuristic_maintenance_overdue() -> None:
    assert heuristic_tool("anything maintenance overdue right now") == "get_overdue_maintenance"


def test_heuristic_none_for_gibberish() -> None:
    assert heuristic_tool("xyzzy plugh") is None
