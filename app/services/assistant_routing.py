"""
Intent scoring and fuzzy routing for the AI assistant.

Scores natural-language paraphrases against tool rules so users are not limited
to exact training phrases.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.assistant_tools import AssistantTools

SCORE_THRESHOLD = 1.0


@dataclass(frozen=True)
class IntentRule:
    name: str
    tool: str
    keywords: tuple[str, ...] = ()
    regexes: tuple[str, ...] = ()
    weight: float = 1.0


INTENT_RULES: tuple[IntentRule, ...] = (
    IntentRule(
        name="high_risk",
        tool="get_high_risk_assets",
        keywords=(
            "high risk",
            "high-risk",
            "at risk",
            "in danger",
            "critical assets",
            "critical asset",
            "unhealthy",
            "failing assets",
            "need attention",
            "needs attention",
            "on alert",
            "high alert",
            "dangerous assets",
            "risky assets",
            "poor health",
            "low health",
            "bad health",
        ),
        regexes=(
            r"\b(risky|dangerous|critical)\b.*\b(asset|fleet|unit|laptop|server)s?\b",
            r"\b(asset|fleet|unit)s?\b.*\b(at risk|high risk|in danger)\b",
        ),
        weight=1.2,
    ),
    IntentRule(
        name="high_risk_by_type",
        tool="get_high_risk_by_type",
        keywords=("unhealthy laptop", "unhealthy server", "risky laptop", "risky printer"),
        regexes=(
            r"\b(unhealthy|risky|failing|critical)\b.*\b(laptop|server|printer|desktop|van|machine)s?\b",
            r"\b(laptop|server|printer)s?\b.*\b(at risk|high risk|unhealthy)\b",
        ),
        weight=1.3,
    ),
    IntentRule(
        name="overdue_maintenance",
        tool="get_overdue_maintenance",
        keywords=(
            "overdue maintenance",
            "maintenance overdue",
            "maintenance is overdue",
            "past due",
            "late maintenance",
            "behind on maintenance",
            "missed maintenance",
        ),
        regexes=(r"\bmaintenance\b.*\b(overdue|past due|late|behind)\b",),
        weight=1.4,
    ),
    IntentRule(
        name="maintenance_this_week",
        tool="get_maintenance_this_week",
        keywords=("maintenance this week", "scheduled this week", "due this week"),
        weight=1.1,
    ),
    IntentRule(
        name="maintenance_recommendations",
        tool="get_maintenance_recommendations",
        keywords=(
            "maintenance recommendations",
            "what maintenance",
            "maintenance needed",
            "service needed",
            "needs maintenance",
        ),
        weight=0.7,
    ),
    IntentRule(
        name="fleet_counts",
        tool="get_fleet_counts",
        keywords=(
            "how many assets",
            "total assets",
            "count of assets",
            "number of assets",
            "fleet size",
            "how many employees",
            "how many departments",
        ),
        regexes=(r"\bhow many\b.*\b(asset|employee|department|fleet)s?\b",),
        weight=1.1,
    ),
    IntentRule(
        name="dashboard_summary",
        tool="get_dashboard_summary",
        keywords=(
            "fleet overview",
            "dashboard summary",
            "give me an overview",
            "operations overview",
            "summary of fleet",
            "how is the fleet",
            "fleet summary",
            "summary please",
        ),
        regexes=(r"\b(overview|summary)\b.*\bfleet\b", r"\bfleet\b.*\b(summary|overview)\b"),
        weight=1.1,
    ),
    IntentRule(
        name="healthy_assets",
        tool="get_healthy_assets",
        keywords=("healthy assets", "good health", "low risk assets", "assets in good shape"),
        weight=1.0,
    ),
    IntentRule(
        name="worst_health",
        tool="get_worst_health_assets",
        keywords=("worst health", "lowest health", "sickest assets", "bottom health"),
        regexes=(r"\bworst\b.*\bhealth\b",),
        weight=1.3,
    ),
    IntentRule(
        name="in_maintenance",
        tool="get_assets_in_maintenance",
        keywords=("in maintenance", "being serviced", "under repair", "currently in maintenance"),
        regexes=(r"\b(asset|assets)\b.*\bin maintenance\b",),
        weight=1.2,
    ),
    IntentRule(
        name="warranty",
        tool="get_warranty_expiring",
        keywords=("warranty expiring", "warranty ending", "warranties due"),
        weight=1.0,
    ),
    IntentRule(
        name="search",
        tool="search_assets",
        keywords=("find asset", "search for", "look up asset", "locate asset"),
        regexes=(r"\bfind\b.*\b(asset|tag|laptop|server)\b",),
        weight=0.9,
    ),
    IntentRule(
        name="help",
        tool="get_help",
        keywords=("help", "what can you do", "what do you know", "commands"),
        weight=0.5,
    ),
)


def _normalize(message: str) -> str:
    return re.sub(r"\s+", " ", message.lower().strip())


def score_message(message: str) -> list[tuple[str, float, str]]:
    """Return sorted list of (tool_name, score, reason)."""
    lower = _normalize(message)
    scores: dict[str, tuple[float, str]] = {}

    for rule in INTENT_RULES:
        rule_score = 0.0
        matched: list[str] = []

        for kw in rule.keywords:
            if kw in lower:
                rule_score += rule.weight
                matched.append(kw)

        for pattern in rule.regexes:
            if re.search(pattern, lower):
                rule_score += rule.weight * 0.9
                matched.append(f"regex:{pattern[:24]}")

        if rule_score > 0:
            prev = scores.get(rule.tool)
            reason = rule.name + (f" ({matched[0]})" if matched else "")
            if prev is None or rule_score > prev[0]:
                scores[rule.tool] = (rule_score, reason)

    ranked = [(tool, sc, reason) for tool, (sc, reason) in scores.items()]
    ranked.sort(key=lambda x: -x[1])
    return ranked


def heuristic_tool(message: str) -> str | None:
    """Last-resort keyword pairing when no rule clears the threshold."""
    lower = _normalize(message)
    risk_words = ("risk", "critical", "danger", "unhealthy", "failing", "alert")
    asset_words = ("asset", "fleet", "unit", "laptop", "server", "printer", "machine")
    maint_words = ("maintenance", "service", "repair")
    overdue_words = ("overdue", "past due", "late", "behind", "due")

    if any(w in lower for w in risk_words) and any(w in lower for w in asset_words):
        if any(t in lower for t in ("laptop", "server", "printer", "desktop", "van", "machine")):
            return "get_high_risk_by_type"
        return "get_high_risk_assets"

    if any(w in lower for w in maint_words) and any(w in lower for w in overdue_words):
        return "get_overdue_maintenance"

    if "how many" in lower and "asset" in lower:
        return "get_fleet_counts"

    if "overview" in lower or ("summary" in lower and "fleet" in lower):
        return "get_dashboard_summary"

    return None


def invoke_tool(tools: AssistantTools, tool_name: str, message: str) -> dict:
    """Dispatch to AssistantTools by method name."""
    dispatch: dict[str, callable] = {
        "get_high_risk_assets": lambda: tools.get_high_risk_assets(),
        "get_high_risk_by_type": lambda: tools.get_high_risk_by_type(message),
        "get_overdue_maintenance": lambda: tools.get_overdue_maintenance(),
        "get_maintenance_this_week": lambda: tools.get_maintenance_this_week(),
        "get_maintenance_recommendations": lambda: tools.get_maintenance_recommendations(),
        "get_fleet_counts": lambda: tools.get_fleet_counts(message),
        "get_dashboard_summary": lambda: tools.get_dashboard_summary(),
        "get_healthy_assets": lambda: tools.get_healthy_assets(),
        "get_worst_health_assets": lambda: tools.get_worst_health_assets(),
        "get_assets_in_maintenance": lambda: tools.get_assets_in_maintenance(),
        "get_warranty_expiring": lambda: tools.get_warranty_expiring(),
        "search_assets": lambda: tools.search_assets(message),
        "get_help": lambda: tools.get_help(),
    }
    fn = dispatch.get(tool_name)
    if fn is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return fn()


def resolve_scored_tool(
    tools: AssistantTools,
    message: str,
    *,
    threshold: float = SCORE_THRESHOLD,
) -> tuple[dict, str | None]:
    """
    Score message and invoke best matching tool, or heuristic fallback.
    Returns (tool_result, tool_name) or ({}, None) if no match.
    """
    ranked = score_message(message)
    if ranked and ranked[0][1] >= threshold:
        tool_name = ranked[0][0]
        return invoke_tool(tools, tool_name, message), tool_name

    heuristic = heuristic_tool(message)
    if heuristic:
        return invoke_tool(tools, heuristic, message), heuristic

    return {}, None
