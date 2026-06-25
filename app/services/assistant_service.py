from __future__ import annotations

import httpx

from app.core.config import settings
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse, AssistantSource
from app.services import narrative as narr
from app.services.assistant_tools import AssistantTools


class AssistantService:
    def __init__(self, tools: AssistantTools) -> None:
        self.tools = tools

    async def chat(self, request: AssistantChatRequest) -> AssistantChatResponse:
        message = request.message.strip()
        tools_used: list[str] = []
        sources: list[AssistantSource] = []

        tool_result, tool_name = self._route_tools(message)
        if tool_name:
            tools_used.append(tool_name)

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

        if settings.assistant_use_ollama:
            try:
                answer = await self._ollama_format(message, tool_result)
            except Exception:
                answer = fallback
        else:
            answer = fallback

        return AssistantChatResponse(answer=answer, tools_used=tools_used, sources=sources)

    def _route_tools(self, message: str) -> tuple[dict, str | None]:
        lower = message.lower().strip()

        if any(k in lower for k in ("help", "what can you", "what do you", "capabilities")):
            return self.tools.get_help(), "get_help"

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
                "worst health",
                "lowest health",
                "poorest health",
                "unhealthiest",
                "bad health",
            )
        ):
            return self.tools.get_worst_health_assets(), "get_worst_health_assets"

        if any(
            k in lower
            for k in (
                "recommend",
                "maintenance",
                "service",
                "repair",
                "needs attention",
                "require maintenance",
            )
        ):
            return self.tools.get_maintenance_recommendations(), "get_maintenance_recommendations"

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
                "employees",
                "employee",
                "laptop",
                "laptops",
                "server",
                "servers",
                "printer",
                "fleet size",
            )
        ):
            return self.tools.get_fleet_counts(message), "get_fleet_counts"

        if any(
            k in lower
            for k in (
                "department",
                "own",
                "most assets",
                "overview",
                "summary",
                "snapshot",
                "operations center",
            )
        ):
            return self.tools.get_dashboard_summary(), "get_dashboard_summary"

        if any(
            k in lower
            for k in (
                "asset",
                "laptop",
                "server",
                "van",
                "printer",
                "search",
                "show",
                "find",
                "where is",
                "location",
            )
        ):
            return self.tools.search_assets(message), "search_assets"

        if len(lower) < 4:
            return self.tools.get_help(), "get_help"

        return self.tools.get_dashboard_summary(), "get_dashboard_summary"

    async def _ollama_format(self, message: str, tool_result: dict) -> str:
        prompt = (
            "You are AssetFlow AI, an operations assistant for non-technical staff.\n"
            "Rewrite the tool data into a short, friendly answer.\n"
            "Rules:\n"
            "- Use plain English; lead with asset names, not codes\n"
            "- Use bullet points when listing multiple items\n"
            "- Keep asset tags in parentheses only when helpful\n"
            "- 2-5 sentences maximum unless listing items\n"
            "- Do not invent data not present in the tool output\n\n"
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
