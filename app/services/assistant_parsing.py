from __future__ import annotations

import re

_ASSET_TAG_RE = re.compile(r"\b([A-Za-z]{2,5}-[A-Za-z]{2,6}-\d{3,5})\b")

_STOP_WORDS = frozenset(
    {
        "show",
        "list",
        "which",
        "what",
        "where",
        "how",
        "many",
        "the",
        "are",
        "is",
        "in",
        "for",
        "at",
        "of",
        "a",
        "an",
        "and",
        "or",
        "me",
        "my",
        "our",
        "all",
        "any",
        "some",
        "recent",
        "currently",
        "right",
        "now",
        "please",
        "assets",
        "asset",
        "department",
        "employee",
        "assigned",
        "assignment",
        "allocations",
        "maintenance",
        "health",
        "status",
        "overdue",
        "completed",
        "scheduled",
    }
)

# Fragments that indicate a comparative/ranking question, not a department name.
_INVALID_DEPT_QUERY_FRAGMENTS = (
    "owns",
    "own the",
    "most",
    "largest",
    "biggest",
    "highest",
    "top ",
    "fewest",
    "least",
    "smallest",
    "lowest",
)


def is_department_ranking_query(message: str) -> bool:
    """True when the user asks which department has the most/fewest assets."""
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "most assets",
            "most asset",
            "owns the most",
            "own the most",
            "largest department",
            "biggest department",
            "top department",
            "which department has",
            "which department owns",
            "department with the most",
            "department with most",
            "fewest assets",
            "least assets",
        )
    )


def _is_valid_department_name_query(query: str) -> bool:
    q = query.lower().strip(" ?.")
    if not q or q in _STOP_WORDS:
        return False
    return not any(frag in q for frag in _INVALID_DEPT_QUERY_FRAGMENTS)


def extract_asset_tag(message: str) -> str | None:
    match = _ASSET_TAG_RE.search(message)
    return match.group(1).upper() if match else None


def extract_department_query(message: str) -> str | None:
    lower = message.lower().strip()
    patterns = (
        r"(?:in|for|at)\s+(?:the\s+)?(.+?)\s+department",
        r"(.+?)\s+department(?:\s+assets|\s+owns|\s+has)?",
        r"department\s+(?:of\s+)?(.+)",
        r"assets\s+in\s+(.+)",
    )
    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            query = match.group(1).strip(" ?.")
            if _is_valid_department_name_query(query):
                return query
    return None


def extract_employee_query(message: str) -> str | None:
    lower = message.lower().strip()
    patterns = (
        r"assigned to\s+(.+)",
        r"assets assigned to\s+(.+)",
        r"(?:what|which)\s+(?:assets|equipment)\s+does\s+(.+?)\s+have",
        r"(.+?)'s assets",
        r"employee\s+(.+)",
        r"for\s+(.+?)\s+(?:employee|staff)",
    )
    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            query = match.group(1).strip(" ?.")
            if query and query not in _STOP_WORDS:
                return query
    return None


def extract_status_query(message: str) -> str | None:
    lower = message.lower()
    if any(k in lower for k in ("in maintenance", "being serviced", "under repair", "being repaired")):
        return "IN_MAINTENANCE"
    if any(k in lower for k in ("available", "unassigned", "in stock", "spare")):
        return "AVAILABLE"
    if any(k in lower for k in ("assigned", "checked out", "in use", "deployed")):
        return "ASSIGNED"
    return None
