from __future__ import annotations

import asyncio
import re
import httpx

from app.core.config import settings
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse, AssistantSource, ChatMessage
from app.services import narrative as narr
from app.services.assistant_tools import AssistantTools
from app.services.assistant_parsing import (
    extract_asset_tag,
    extract_department_query,
    extract_employee_query,
    extract_status_query,
    is_department_ranking_query,
)

_OLLAMA_FORMAT_TIMEOUT_SECONDS = 35.0


class AssistantService:
    def __init__(self, tools: AssistantTools) -> None:
        self.tools = tools

    async def chat(self, request: AssistantChatRequest) -> AssistantChatResponse:
        message = request.message.strip()
        history = request.history

        # Heuristic for follow-up questions referencing history context.
        # If the query contains pronouns or follow-up keywords and we have history,
        # we append the context from the previous user message.
        routing_message = message
        lower = message.lower().strip()
        if history and len(history) >= 2:
            last_user_msg = next((m.content for m in reversed(history) if m.role == "user"), "")
            if any(p in lower for p in ("they", "them", "it", "why", "those", "these", "explain", "detail", "describe")):
                routing_message = f"{last_user_msg} {message}"

        tool_result, tool_name = await asyncio.to_thread(self._route_tools, routing_message)

        tools_used: list[str] = []
        if tool_name:
            tools_used.append(tool_name)

        sources: list[AssistantSource] = []
        if tool_result.get("sources"):
            for s in tool_result["sources"]:
                sources.append(AssistantSource(**s))

        fallback = tool_result.get("fallback_answer", narr.assistant_capabilities_message())

        if not settings.assistant_enabled:
            return AssistantChatResponse(
                answer=fallback,
                tools_used=tools_used,
                sources=sources,
            )

        use_fallback = _should_use_fallback_answer(tool_result)

        if settings.assistant_use_ollama and not use_fallback:
            try:
                answer = await asyncio.wait_for(
                    self._ollama_format(message, tool_result, history),
                    timeout=min(settings.ollama_timeout_seconds, _OLLAMA_FORMAT_TIMEOUT_SECONDS),
                )
                if not _validate_ollama_output(answer, tool_result.get("data_text", "")):
                    answer = fallback
            except (asyncio.TimeoutError, Exception):
                answer = fallback
        else:
            answer = fallback

        return AssistantChatResponse(answer=answer, tools_used=tools_used, sources=sources)

    def _route_tools(self, message: str) -> tuple[dict, str | None]:
        lower = message.lower().strip()

        if any(k in lower for k in ("help", "what can you", "what do you", "capabilities")):
            return self.tools.get_help(), "get_help"

        asset_tag = extract_asset_tag(message)
        if asset_tag and any(
            k in lower
            for k in (
                "health",
                "condition",
                "risk",
                "score",
                "how is",
                "status of",
                "predicted",
            )
        ):
            return self.tools.get_asset_health_detail(message), "get_asset_health_detail"

        if any(
            k in lower
            for k in (
                "high risk",
                "high-risk",
                "risky",
                "at risk",
                "critical health",
                "dangerous",
            )
        ):
            return self.tools.get_high_risk_assets(), "get_high_risk_assets"

        if any(
            k in lower
            for k in (
                "good condition",
                "healthy",
                "good health",
                "best health",
                "high health",
                "low risk",
                "lowest risk",
                "safe",
                "working condition",
            )
        ):
            return self.tools.get_healthy_assets(), "get_healthy_assets"

        if any(
            k in lower
            for k in (
                "worst health",
                "lowest health",
                "poorest health",
                "unhealthiest",
                "bad health",
            )
        ):
            return self.tools.get_worst_health_assets(), "get_worst_health_assets"

        if any(k in lower for k in ("overdue", "past due", "late maintenance", "due maintenance")):
            return self.tools.get_overdue_maintenance(), "get_overdue_maintenance"

        if any(
            k in lower
            for k in ("in maintenance", "being serviced", "under repair", "being repaired")
        ):
            return self.tools.get_assets_in_maintenance(), "get_assets_in_maintenance"

        if any(
            k in lower
            for k in (
                "completed maintenance",
                "maintenance completed",
                "finished maintenance",
                "recently serviced",
            )
        ):
            return self.tools.get_recent_completed_maintenance(), "get_recent_completed_maintenance"

        employee_query = extract_employee_query(message)
        if employee_query:
            return self.tools.get_employee_assets(message), "get_employee_assets"

        if any(
            k in lower
            for k in (
                "assigned to",
                "who has",
                "employee assets",
                "staff assets",
            )
        ):
            return self.tools.get_employee_assets(message), "get_employee_assets"

        if is_department_ranking_query(message) or any(
            k in lower
            for k in (
                "most assets",
                "overview",
                "summary",
                "snapshot",
                "operations center",
            )
        ):
            return self.tools.get_dashboard_summary(), "get_dashboard_summary"

        if extract_status_query(message):
            return self.tools.get_assets_by_status(message), "get_assets_by_status"

        dept_query = extract_department_query(message)
        if dept_query or any(
            k in lower for k in ("department", "assets in", "dept ")
        ):
            return self.tools.get_department_assets(message), "get_department_assets"

        if any(
            k in lower
            for k in (
                "recommend",
                "needs attention",
                "ai recommendation",
                "what should we fix",
            )
        ):
            return self.tools.get_maintenance_recommendations(), "get_maintenance_recommendations"

        if any(
            k in lower
            for k in (
                "maintenance",
                "service",
                "repair",
                "require maintenance",
            )
        ):
            return self.tools.get_maintenance_recommendations(), "get_maintenance_recommendations"

        if any(
            k in lower
            for k in (
                "allocation",
                "assigned",
                "assignment",
                "checked out",
                "who got",
            )
        ):
            return self.tools.get_recent_allocations(), "get_recent_allocations"

        if any(k in lower for k in ("transfer", "moved", "relocated", "reassign department")):
            return self.tools.get_recent_transfers(), "get_recent_transfers"

        if any(k in lower for k in ("warranty", "warranties", "expiring", "expire")):
            return self.tools.get_warranty_expiring(), "get_warranty_expiring"

        if any(
            k in lower
            for k in (
                "how many",
                "count",
                "total",
                "number of",
                "fleet size",
            )
        ):
            return self.tools.get_fleet_counts(message), "get_fleet_counts"

        if any(
            k in lower
            for k in (
                "search",
                "find",
                "where is",
                "location",
                "show",
            )
        ):
            return self.tools.search_assets(message), "search_assets"

        if any(
            k in lower
            for k in (
                "employees",
                "employee",
                "laptop",
                "laptops",
                "server",
                "servers",
                "printer",
            )
        ):
            return self.tools.get_fleet_counts(message), "get_fleet_counts"

        if any(
            k in lower
            for k in (
                "asset",
                "van",
            )
        ):
            return self.tools.search_assets(message), "search_assets"

        if len(lower) < 4:
            return self.tools.get_help(), "get_help"

        return self.tools.get_dashboard_summary(), "get_dashboard_summary"

    async def _ollama_format(self, message: str, tool_result: dict, history: list[ChatMessage] = []) -> str:
        history_str = ""
        for msg in history:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_str += f"{role_label}: {msg.content}\n"

        prompt = (
            "You are AssetFlow AI, an operations assistant for non-technical staff.\n"
            "Rewrite the tool data into a short, friendly answer.\n"
            "Rules:\n"
            "- Use plain English; lead with asset names, not codes\n"
            "- Use bullet points when listing multiple items\n"
            "- Keep asset tags in parentheses only when helpful\n"
            "- 2-5 sentences maximum unless listing items\n"
            "- Do not invent data not present in the tool output\n\n"
            f"Conversation History:\n{history_str}\n"
            f"User question: {message}\n"
            f"Tool data: {tool_result.get('data_text', '')}\n"
        )
        timeout = settings.ollama_timeout_seconds
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={"model": settings.ollama_model, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()
            payload = response.json()
            text = (payload.get("response") or "").strip()
            if not text:
                return tool_result.get("fallback_answer", narr.assistant_capabilities_message())
            return text


def _should_use_fallback_answer(tool_result: dict) -> bool:
    """Use the template fallback when Ollama would likely dilute grounded DB data."""
    if tool_result.get("skip_ollama"):
        return True
    if tool_result.get("cache_required"):
        return True
    data = tool_result.get("data_text", "").lower()
    if any(
        phrase in data
        for phrase in (
            "no department matched",
            "no employee matched",
            "no assets matched",
            "no search query detected",
            "no employee name detected",
        )
    ):
        return True
    return False


def _validate_ollama_output(ollama_text: str, data_text: str) -> bool:
    """
    Validates that the Ollama narrative output does not omit critical database
    identifiers (asset tags) or health percentages.
    """
    if not data_text:
        return True
    if not ollama_text:
        return False

    # 1. Validate Asset Tags
    tags = re.findall(r"\b[A-Za-z]{2,5}-[A-Za-z]{2,6}-\d{3,5}\b", data_text)
    for tag in tags:
        if tag.lower() not in ollama_text.lower():
            return False

    # 2. Validate Health Percentages (e.g. 4%, 92%)
    pcts = re.findall(r"(\d+)%", data_text)
    for pct in pcts:
        if pct not in ollama_text:
            return False

    return True
