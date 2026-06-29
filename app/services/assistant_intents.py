"""
Intent helpers for assistant tool routing.

Each function detects a specific enterprise question pattern from natural language.
"""
from __future__ import annotations

import re

from app.services.assistant_parsing import (
    extract_asset_tag,
    extract_department_query,
    extract_employee_query,
    extract_status_query,
    is_contextual_follow_up,
    is_department_ranking_query,
    is_high_risk_query,
)

_ASSET_TYPE_ALIASES: dict[str, str] = {
    "laptop": "Laptop",
    "laptops": "Laptop",
    "desktop": "Desktop Workstation",
    "desktops": "Desktop Workstation",
    "workstation": "Desktop Workstation",
    "workstations": "Desktop Workstation",
    "server": "Server",
    "servers": "Server",
    "printer": "Printer",
    "printers": "Printer",
    "monitor": "Monitor",
    "monitors": "Monitor",
    "van": "Delivery Van",
    "vans": "Delivery Van",
    "vehicle": "Company Vehicle",
    "vehicles": "Company Vehicle",
    "machine": "Production Machine",
    "machines": "Production Machine",
}

_SEARCH_STOP_WORDS = frozenset(
    {
        "show",
        "which",
        "what",
        "where",
        "find",
        "search",
        "list",
        "assets",
        "asset",
        "many",
        "how",
        "the",
        "are",
        "there",
        "all",
        "any",
        "some",
        "currently",
        "right",
        "now",
        "please",
        "high",
        "risk",
        "alert",
        "healthy",
        "health",
        "poor",
        "bad",
        "critical",
        "dangerous",
        "this",
        "that",
        "week",
        "month",
        "today",
        "overdue",
        "due",
        "require",
        "requires",
        "requiring",
        "need",
        "needs",
        "needing",
        "maintenance",
        "service",
        "repair",
        "belong",
        "belongs",
        "belonging",
        "department",
        "dept",
        "employee",
        "staff",
        "available",
        "assigned",
        "expiring",
        "expire",
        "warranty",
        "warranties",
        "transferred",
        "transfer",
        "recent",
        "recently",
        "most",
        "fewest",
        "count",
        "total",
        "number",
        "fleet",
        "size",
    }
)


def extract_asset_type_query(message: str) -> str | None:
    lower = message.lower()
    best: tuple[int, str] | None = None
    for alias, type_name in _ASSET_TYPE_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", lower):
            if best is None or len(alias) > best[0]:
                best = (len(alias), type_name)
    return best[1] if best else None


def extract_type_and_department(message: str) -> tuple[str | None, str | None]:
    """Return (asset_type_name, department_query) when both appear in a question."""
    type_name = extract_asset_type_query(message)
    dept_query = extract_department_query(message)
    if type_name and dept_query:
        return type_name, dept_query

    lower = message.lower().strip()
    patterns = (
        r"(?:which|what|show|list)\s+(?:\w+\s+){0,3}(laptops|servers|desktops|printers|monitors|vans|vehicles|machines)\s+(?:belong(?:s|ing)?\s+to|in|for|at|are\s+in)\s+(?:the\s+)?(.+?)(?:\?|$)",
        r"(laptops|servers|desktops|printers|monitors|vans|vehicles|machines)\s+(?:in|for|at|belong(?:s|ing)?\s+to|are\s+in)\s+(?:the\s+)?(.+?)(?:\?|$|department)",
        r"(?:which|what)\s+(laptops|servers|desktops|printers|monitors|vans|vehicles|machines)\s+(?:are\s+)?in\s+(?:the\s+)?(.+?)(?:\?|$|department)",
    )
    for pattern in patterns:
        match = re.search(pattern, lower)
        if not match:
            continue
        alias = match.group(1).strip()
        dept = match.group(2).strip(" ?.")
        if any(
            bad in dept
            for bad in (
                "poor health",
                "bad health",
                "high risk",
                "low health",
                "good health",
                "critical",
                "high alert",
            )
        ):
            continue
        type_from_alias = _ASSET_TYPE_ALIASES.get(alias)
        if type_from_alias and dept and dept not in _SEARCH_STOP_WORDS:
            return type_from_alias, dept
    return type_name, dept_query


def is_department_maintenance_ranking_query(message: str) -> bool:
    if is_contextual_follow_up(message):
        return False
    lower = message.lower().strip()
    if "department" not in lower and "dept" not in lower:
        return False
    return any(
        k in lower
        for k in (
            "most maintenance",
            "most service",
            "most repair",
            "most repairs",
            "most open maintenance",
            "maintenance requests",
            "maintenance records",
            "service requests",
            "open maintenance",
        )
    ) and any(k in lower for k in ("most", "top", "highest", "largest"))


def is_maintenance_this_week_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "this week",
            "next 7 days",
            "next seven days",
            "due this week",
            "scheduled this week",
            "within the week",
        )
    ) and any(k in lower for k in ("maintenance", "service", "repair", "serviced"))


def is_warranty_this_month_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(k in lower for k in ("warranty", "warranties")) and any(
        k in lower for k in ("this month", "expire this month", "expiring this month")
    )


def is_poor_health_type_query(message: str) -> bool:
    if not extract_asset_type_query(message):
        return False
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "poor health",
            "bad health",
            "low health",
            "unhealthy",
            "worst health",
            "critical",
            "high risk",
            "high-risk",
            "at risk",
            "high alert",
        )
    )


def is_available_assets_query(message: str) -> bool:
    if extract_status_query(message) == "AVAILABLE":
        return True
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "available assets",
            "assets available",
            "in stock",
            "unassigned assets",
            "spare assets",
            "free assets",
        )
    )


def is_assigned_assets_query(message: str) -> bool:
    if extract_employee_query(message):
        return False
    if extract_status_query(message) == "ASSIGNED":
        return True
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "assigned assets",
            "assets assigned",
            "checked out",
            "in use",
            "deployed assets",
        )
    ) and "department" not in lower


def is_recent_activity_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "recent activity",
            "what happened",
            "latest activity",
            "recent events",
            "activity feed",
        )
    )


def is_type_count_query(message: str) -> bool:
    lower = message.lower().strip()
    if not extract_asset_type_query(message):
        return False
    return any(
        k in lower
        for k in ("how many", "count", "number of", "total")
    )


def is_help_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower for k in ("help", "what can you", "what do you", "capabilities")
    )


def is_overview_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower for k in ("overview", "summary", "snapshot", "operations center")
    )


def is_transfer_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "transfer",
            "transferred",
            "relocated",
            "reassign department",
            "moved department",
            "moved to",
            "moved recently",
            "what moved",
        )
    )


def is_allocation_query(message: str) -> bool:
    lower = message.lower().strip()
    if extract_employee_query(message):
        return False
    return any(
        k in lower
        for k in (
            "allocation",
            "allocations",
            "assignment",
            "assignments",
            "checked out",
            "who got",
            "recent assignment",
            "recent assignments",
            "recently assigned",
            "asset assignments",
        )
    )


def is_warranty_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(k in lower for k in ("warranty", "warranties", "expiring", "expire"))


def is_maintenance_recommendation_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "recommend",
            "needs attention",
            "ai recommendation",
            "what should we fix",
            "require maintenance",
            "requires maintenance",
            "requiring maintenance",
            "need maintenance",
            "needs maintenance",
            "need service",
            "needs service",
        )
    )


def is_overdue_maintenance_query(message: str) -> bool:
    lower = message.lower().strip()
    if is_maintenance_this_week_query(message):
        return False
    return any(
        k in lower
        for k in ("overdue", "past due", "late maintenance", "due maintenance", "due today")
    )


def is_completed_maintenance_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "completed maintenance",
            "maintenance completed",
            "finished maintenance",
            "recently serviced",
            "recently completed",
        )
    )


def is_in_maintenance_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in ("in maintenance", "being serviced", "under repair", "being repaired")
    )


def is_healthy_assets_query(message: str) -> bool:
    lower = message.lower().strip()
    if is_high_risk_query(message) or is_poor_health_type_query(message):
        return False
    return any(
        k in lower
        for k in (
            "good condition",
            "healthy assets",
            "good health",
            "best health",
            "high health",
            "low risk",
            "lowest risk",
            "safe assets",
            "working condition",
        )
    )


def is_worst_health_query(message: str) -> bool:
    if is_poor_health_type_query(message):
        return False
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "worst health",
            "lowest health",
            "poorest health",
            "unhealthiest",
            "bad health",
        )
    )


def is_fleet_count_query(message: str) -> bool:
    lower = message.lower().strip()
    if is_type_count_query(message):
        return True
    return any(
        k in lower for k in ("how many", "count", "total", "number of", "fleet size")
    )


def is_search_query(message: str) -> bool:
    lower = message.lower().strip()
    if extract_asset_tag(message):
        return True
    return any(
        k in lower for k in ("search", "find", "where is", "where are", "locate", "location of")
    )


def is_generic_maintenance_query(message: str) -> bool:
    lower = message.lower().strip()
    if (
        is_maintenance_this_week_query(message)
        or is_overdue_maintenance_query(message)
        or is_completed_maintenance_query(message)
        or is_in_maintenance_query(message)
        or is_maintenance_recommendation_query(message)
    ):
        return False
    return any(k in lower for k in ("maintenance", "service", "repair"))


def is_department_assets_query(message: str) -> bool:
    if is_department_ranking_query(message) or is_department_maintenance_ranking_query(message):
        return False
    type_name, dept = extract_type_and_department(message)
    if type_name and dept:
        return False
    lower = message.lower().strip()
    if any(k in lower for k in ("department have", "department has", "department owns")):
        return True
    if extract_department_query(message):
        return True
    return any(k in lower for k in ("department", "assets in", "dept "))


def extract_search_term(message: str) -> str:
    if tag := extract_asset_tag(message):
        return tag
    tokens = re.findall(r"[A-Za-z0-9-]+", message)
    for token in tokens:
        if len(token) >= 3 and token.lower() not in _SEARCH_STOP_WORDS:
            return token
    return ""
