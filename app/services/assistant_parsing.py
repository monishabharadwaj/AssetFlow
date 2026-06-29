from __future__ import annotations

import re
from dataclasses import dataclass

_ASSET_TAG_RE = re.compile(r"\b([A-Za-z]{2,5}-[A-Za-z]{2,6}-\d{3,5})\b")

_FOLLOW_UP_PRONOUNS = (
    "they",
    "them",
    "it",
    "its",
    "that",
    "this",
    "those",
    "these",
    "same",
    "previous",
)

_FOLLOW_UP_PHRASES = (
    "that asset",
    "that server",
    "that laptop",
    "the previous",
    "the same",
    "previous one",
    "previous asset",
)

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
    if any(
        k in lower
        for k in (
            "most maintenance",
            "most service",
            "most repair",
            "maintenance requests",
        )
    ):
        return False
    if is_contextual_follow_up(message):
        return False
    return any(
        k in lower
        for k in (
            "most assets",
            "most asset",
            "owns the most",
            "own the most",
            "owns most",
            "own most",
            "largest department",
            "biggest department",
            "top department",
            "department with the most",
            "department with most",
            "fewest assets",
            "least assets",
            "smallest department",
            "lowest department",
            "which department has the most",
            "which department has most",
            "which department owns the most",
            "which department owns most",
        )
    )


def department_ranking_mode(message: str) -> str:
    """Return 'fewest' or 'most' for department asset ranking questions."""
    lower = message.lower().strip()
    if any(
        k in lower
        for k in (
            "fewest",
            "least",
            "smallest",
            "lowest",
            "minimum",
        )
    ):
        return "fewest"
    return "most"


@dataclass(frozen=True)
class SessionContext:
    last_asset_tag: str | None = None


def extract_session_context(history: list) -> SessionContext:
    """Resolve the focused asset from prior assistant/user turns (single-asset replies only)."""
    for msg in reversed(history):
        role = msg.role if hasattr(msg, "role") else msg.get("role")
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        if role != "assistant" or not content:
            continue
        tags = [m.group(1).upper() for m in _ASSET_TAG_RE.finditer(content)]
        if len(tags) == 1:
            return SessionContext(last_asset_tag=tags[0])
        if len(tags) > 1:
            return SessionContext(last_asset_tag=None)
    for msg in reversed(history):
        role = msg.role if hasattr(msg, "role") else msg.get("role")
        content = msg.content if hasattr(msg, "content") else msg.get("content", "")
        if role != "user" or not content:
            continue
        tags = [m.group(1).upper() for m in _ASSET_TAG_RE.finditer(content)]
        if len(tags) == 1:
            return SessionContext(last_asset_tag=tags[0])
    return SessionContext(last_asset_tag=None)


def is_contextual_follow_up(message: str) -> bool:
    """True when the user refers to a prior turn without naming an entity."""
    if extract_asset_tag(message):
        return False
    lower = message.lower().strip()
    if any(phrase in lower for phrase in _FOLLOW_UP_PHRASES):
        return True
    return any(
        re.search(rf"\b{re.escape(word)}\b", lower) for word in _FOLLOW_UP_PRONOUNS
    )


def is_standalone_query(message: str) -> bool:
    """True when the message is a new question, not a pronoun follow-up."""
    if is_contextual_follow_up(message):
        return False
    lower = message.lower().strip()
    if is_department_ranking_query(message):
        return True
    if any(
        k in lower
        for k in (
            "high risk",
            "high-risk",
            "high alert",
            "on alert",
            "at risk",
            "critical",
            "how many",
            "how much",
            "fleet size",
            "transferred",
            "transfer",
            "maintenance",
            "warranty",
            "overview",
            "summary",
            "snapshot",
        )
    ):
        return True
    if re.search(r"\b(which|what|show|list|find)\s+(assets|servers|laptops|printers)\b", lower):
        return True
    return False


def is_high_risk_query(message: str) -> bool:
    lower = message.lower().strip()
    return any(
        k in lower
        for k in (
            "high risk",
            "high-risk",
            "high alert",
            "on alert",
            "at risk",
            "risky",
            "critical health",
            "dangerous",
            "critical assets",
            "critical asset",
        )
    )


def is_plural_follow_up(message: str) -> bool:
    lower = message.lower().strip()
    return any(re.search(rf"\b{word}\b", lower) for word in ("they", "them", "those", "these"))


def resolve_follow_up(message: str, ctx: SessionContext) -> tuple[str, str] | None:
    """
    Map a contextual follow-up to (tool_name, tool_argument).
    tool_argument is an asset tag or a synthetic message for health lookup.
    """
    if not ctx.last_asset_tag or is_standalone_query(message):
        return None

    if not is_contextual_follow_up(message):
        return None

    lower = message.lower().strip()
    tag = ctx.last_asset_tag

    if is_plural_follow_up(message) and not any(
        k in lower for k in ("department", "dept", "assigned", "assignee", "who")
    ):
        return None

    if is_department_ranking_query(message):
        return None

    if any(
        k in lower
        for k in (
            "department",
            "dept",
            "belongs to",
            "owned by",
        )
    ):
        return ("get_asset_department", tag)

    if any(
        k in lower
        for k in (
            "assigned",
            "assignee",
            "who has",
            "who is",
            "employee",
            "staff member",
            "staff",
        )
    ):
        return ("get_asset_assignee", tag)

    if any(
        k in lower
        for k in (
            "health",
            "condition",
            "score",
            "explain",
            "why",
            "detail",
            "describe",
        )
    ) or (re.search(r"\b(it|that|this)\b", lower) and "risk" in lower):
        return ("get_asset_health_detail", f"What is the health of {tag}?")

    return None


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
        r"(?:laptops|servers|desktops|printers|monitors|vans|vehicles|machines|assets|equipment)\s+(?:belong(?:s|ing)?\s+to|in|for|at)\s+(?:the\s+)?(.+?)(?:\?|$|department)",
        r"(?:belong(?:s|ing)?\s+to|in|for|at)\s+(?:the\s+)?(.+?)\s+department",
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
            if query and query not in _STOP_WORDS and "department" not in query:
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
