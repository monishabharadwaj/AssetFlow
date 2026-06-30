from __future__ import annotations

import asyncio
import re
import httpx

from app.core.config import settings
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse, AssistantSource, ChatMessage
from app.services import narrative as narr
from app.services.assistant_routing import resolve_scored_tool
from app.services.assistant_tools import AssistantTools
from app.services.assistant_parsing import (
    extract_asset_tag,
    extract_employee_query,
    extract_session_context,
    is_contextual_follow_up,
    is_department_ranking_query,
    is_high_risk_query,
    is_plural_follow_up,
    resolve_follow_up,
)
from app.services.assistant_intents import (
    extract_type_and_department,
    is_allocation_query,
    is_assigned_assets_query,
    is_available_assets_query,
    is_completed_maintenance_query,
    is_department_assets_query,
    is_department_maintenance_ranking_query,
    is_fleet_count_query,
    is_generic_maintenance_query,
    is_healthy_assets_query,
    is_help_query,
    is_in_maintenance_query,
    is_maintenance_recommendation_query,
    is_maintenance_this_week_query,
    is_overdue_maintenance_query,
    is_overview_query,
    is_poor_health_type_query,
    is_search_query,
    is_transfer_query,
    is_warranty_query,
    is_warranty_this_month_query,
    is_worst_health_query,
)

_OLLAMA_FORMAT_TIMEOUT_SECONDS = 35.0

_HISTORY_EXPAND_WORDS = (
    "they",
    "them",
    "why",
    "those",
    "these",
    "explain",
    "detail",
    "describe",
)


class AssistantService:
    def __init__(self, tools: AssistantTools) -> None:
        self.tools = tools

    async def chat(self, request: AssistantChatRequest) -> AssistantChatResponse:
        message = request.message.strip()
        history = request.history

        tool_result, tool_name = await asyncio.to_thread(
            self._dispatch_tools,
            message,
            history,
        )

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
                ctx = extract_session_context(history)
                answer = await asyncio.wait_for(
                    self._ollama_format(
                        message,
                        tool_result,
                        history,
                        tool_name=tool_name,
                        focus_asset_tag=ctx.last_asset_tag,
                    ),
                    timeout=min(settings.ollama_timeout_seconds, _OLLAMA_FORMAT_TIMEOUT_SECONDS),
                )
                validation = tool_result.get("ollama_validation", "relaxed")
                if not _validate_ollama_output(
                    answer,
                    tool_result.get("data_text", ""),
                    validation=validation,
                ):
                    answer = fallback
            except (asyncio.TimeoutError, Exception):
                answer = fallback
        else:
            answer = fallback

        return AssistantChatResponse(answer=answer, tools_used=tools_used, sources=sources)

    def _dispatch_tools(
        self,
        message: str,
        history: list[ChatMessage],
    ) -> tuple[dict, str | None]:
        ctx = extract_session_context(history)

        follow_up = resolve_follow_up(message, ctx)
        if follow_up:
            tool_name, tool_arg = follow_up
            return self._invoke_tool(tool_name, tool_arg)

        routing_message = self._expand_routing_message(message, history, ctx)
        return self._route_tools(routing_message)

    def _invoke_tool(self, tool_name: str, tool_arg: str) -> tuple[dict, str]:
        if tool_name == "get_asset_department":
            return self.tools.get_asset_department(tool_arg), tool_name
        if tool_name == "get_asset_assignee":
            return self.tools.get_asset_assignee(tool_arg), tool_name
        if tool_name == "get_asset_health_detail":
            return self.tools.get_asset_health_detail(tool_arg), tool_name
        return self.tools.get_clarification(), "get_clarification"

    @staticmethod
    def _expand_routing_message(
        message: str,
        history: list[ChatMessage],
        ctx,
    ) -> str:
        lower = message.lower().strip()

        if ctx.last_asset_tag and is_contextual_follow_up(message) and not is_plural_follow_up(message):
            return f"Asset {ctx.last_asset_tag}: {message}"

        if history and len(history) >= 2:
            last_user_msg = next(
                (m.content for m in reversed(history) if m.role == "user"),
                "",
            )
            if last_user_msg and any(p in lower for p in _HISTORY_EXPAND_WORDS):
                if is_plural_follow_up(message) or any(
                    w in lower for w in ("explain", "why", "detail", "describe")
                ):
                    return f"{last_user_msg} {message}"

        return message

    def _route_tools(self, message: str) -> tuple[dict, str | None]:
        if is_help_query(message):
            return self.tools.get_help(), "get_help"

        if is_department_ranking_query(message):
            return self.tools.get_department_ranking(message), "get_department_ranking"

        if is_department_maintenance_ranking_query(message):
            return self.tools.get_department_maintenance_ranking(), "get_department_maintenance_ranking"

        if is_poor_health_type_query(message):
            return self.tools.get_high_risk_by_type(message), "get_high_risk_by_type"

        type_name, dept_query = extract_type_and_department(message)
        if type_name and dept_query:
            return (
                self.tools.get_assets_by_department_and_type(message),
                "get_assets_by_department_and_type",
            )

        if is_high_risk_query(message):
            return self.tools.get_high_risk_assets(), "get_high_risk_assets"

        asset_tag = extract_asset_tag(message)
        lower = message.lower().strip()
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

        if is_healthy_assets_query(message):
            return self.tools.get_healthy_assets(), "get_healthy_assets"

        if is_worst_health_query(message):
            return self.tools.get_worst_health_assets(), "get_worst_health_assets"

        if is_maintenance_this_week_query(message):
            return self.tools.get_maintenance_this_week(), "get_maintenance_this_week"

        if is_overdue_maintenance_query(message):
            return self.tools.get_overdue_maintenance(), "get_overdue_maintenance"

        if is_in_maintenance_query(message):
            return self.tools.get_assets_in_maintenance(), "get_assets_in_maintenance"

        if is_completed_maintenance_query(message):
            return self.tools.get_recent_completed_maintenance(), "get_recent_completed_maintenance"

        if is_department_assets_query(message):
            return self.tools.get_department_assets(message), "get_department_assets"

        if extract_employee_query(message):
            return self.tools.get_employee_assets(message), "get_employee_assets"

        if is_overview_query(message):
            return self.tools.get_dashboard_summary(), "get_dashboard_summary"

        if is_available_assets_query(message):
            return self.tools.get_assets_by_status(message), "get_assets_by_status"

        if is_assigned_assets_query(message):
            return self.tools.get_assets_by_status(message), "get_assets_by_status"

        if is_maintenance_recommendation_query(message):
            return self.tools.get_maintenance_recommendations(), "get_maintenance_recommendations"

        if is_generic_maintenance_query(message):
            return self.tools.get_maintenance_recommendations(), "get_maintenance_recommendations"

        if is_allocation_query(message):
            return self.tools.get_recent_allocations(), "get_recent_allocations"

        if is_transfer_query(message):
            return self.tools.get_recent_transfers(), "get_recent_transfers"

        if is_warranty_this_month_query(message):
            return self.tools.get_warranty_this_month(), "get_warranty_this_month"

        if is_warranty_query(message):
            return self.tools.get_warranty_expiring(), "get_warranty_expiring"

        if is_fleet_count_query(message):
            return self.tools.get_fleet_counts(message), "get_fleet_counts"

        if is_search_query(message):
            return self.tools.search_assets(message), "search_assets"

        scored_result, scored_tool = resolve_scored_tool(self.tools, message)
        if scored_tool:
            return scored_result, scored_tool

        if len(lower) < 4:
            return self.tools.get_help(), "get_help"

        return self.tools.get_clarification(), "get_clarification"

    async def _ollama_format(
        self,
        message: str,
        tool_result: dict,
        history: list[ChatMessage] | None = None,
        *,
        tool_name: str | None = None,
        focus_asset_tag: str | None = None,
    ) -> str:
        history = history or []
        history_str = ""
        for msg in history[-8:]:
            role_label = "User" if msg.role == "user" else "Assistant"
            history_str += f"{role_label}: {msg.content}\n"

        focus_line = ""
        if focus_asset_tag:
            focus_line = f"Conversation focus asset: {focus_asset_tag}\n"

        tool_hint = ""
        if tool_name in {"get_department_ranking", "get_asset_department", "get_asset_assignee"}:
            tool_hint = (
                "Answer in 1-2 short sentences. Give ONLY what the user asked for. "
                "Do not add fleet overview or extra statistics.\n"
            )
        elif tool_name == "get_dashboard_summary":
            tool_hint = "The user asked for an overview — a brief summary with bullets is fine.\n"
        elif tool_name in {"get_high_risk_assets", "get_healthy_assets", "get_worst_health_assets"}:
            tool_hint = (
                "List the assets clearly. Keep every asset tag and health percentage from the tool data.\n"
            )

        prompt = (
            "You are AssetFlow AI, a friendly enterprise asset operations assistant.\n"
            "You receive verified database facts. Rewrite them into a natural, conversational reply.\n"
            "Rules:\n"
            "- Answer ONLY the user's latest question — do not dump unrelated fleet data\n"
            "- Use plain English; prefer asset names over codes when both are available\n"
            "- Use bullet points only when listing multiple items\n"
            "- Keep asset tags when they appear in the tool data\n"
            "- Do not invent facts, numbers, names, or tags not in the tool data\n"
            "- Respect conversation history for follow-ups (e.g. 'it', 'that asset')\n"
            f"{tool_hint}\n"
            f"{focus_line}"
            f"Conversation history:\n{history_str or '(none)'}\n"
            f"User question: {message}\n"
            f"Verified tool data:\n{tool_result.get('data_text', '')}\n"
            "Reply:"
        )
        timeout = settings.ollama_timeout_seconds
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
            )
            response.raise_for_status()
            payload = response.json()
            text = (payload.get("response") or "").strip()
            if not text:
                return tool_result.get("fallback_answer", narr.assistant_capabilities_message())
            return text


def _should_use_fallback_answer(tool_result: dict) -> bool:
    """Use the template fallback when Ollama should not run or would be unsafe."""
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
            "no asset matched",
            "no search query detected",
            "no employee name detected",
            "no asset tag found",
            "no departments with",
            "prediction cache is empty",
            "clarification requested",
            "assistant capabilities",
        )
    ):
        return True
    return False


def _validate_ollama_output(
    ollama_text: str,
    data_text: str,
    *,
    validation: str = "relaxed",
) -> bool:
    """
    Validates Ollama output against grounded tool data.
    - strict: every asset tag and health % from data_text must appear
    - relaxed: primary tag (if any) and single-asset health % must appear
    - minimal: key numbers and a recognizable name fragment must appear
    """
    if not data_text:
        return True
    if not ollama_text:
        return False
    if validation == "off":
        return True

    ollama_lower = ollama_text.lower()
    tags = re.findall(r"\b[A-Za-z]{2,5}-[A-Za-z]{2,6}-\d{3,5}\b", data_text)
    pcts = re.findall(r"(\d+)%", data_text)

    if validation == "strict":
        for tag in tags:
            if tag.lower() not in ollama_lower:
                return False
        for pct in pcts:
            if pct not in ollama_text:
                return False
        return True

    if validation == "minimal":
        numbers = re.findall(r"\b(\d+)\b", data_text)
        for num in numbers[:2]:
            if num not in ollama_text:
                return False

        if "->" in data_text:
            _, right = data_text.split("->", 1)
            label = right.strip()
            if label and label.lower() not in ollama_lower:
                token = label.split("&")[0].strip().split()[0]
                if len(token) >= 3 and token.lower() not in ollama_lower:
                    return False
        elif "assignee=" in data_text.lower():
            assignee = data_text.split("assignee=", 1)[1].strip()
            if assignee.lower() != "unassigned":
                token = assignee.split()[0]
                if len(token) >= 2 and token.lower() not in ollama_lower:
                    return False
        elif ":" in data_text:
            dept_name = data_text.split(":", 1)[0].strip()
            if len(dept_name) >= 3 and dept_name.lower() not in ollama_lower:
                token = dept_name.split()[0]
                if len(token) >= 3 and token.lower() not in ollama_lower:
                    return False

        if tags and tags[0].lower() not in ollama_lower:
            return False
        return True

    # relaxed (default)
    if tags and tags[0].lower() not in ollama_lower:
        return False
    if pcts and len(tags) <= 1:
        if pcts[0] not in ollama_text:
            return False
    elif validation == "relaxed" and len(tags) > 1 and pcts:
        if pcts[0] not in ollama_text:
            return False
    return True
