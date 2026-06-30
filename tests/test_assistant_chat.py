"""Assistant chat reliability — Ollama on with graceful fallback."""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.assistant import AssistantChatRequest
from app.services.assistant_service import AssistantService
from app.services.ollama_client import reset_ollama_probe_cache


def _overdue_tool_result() -> dict:
    return {
        "data_text": "IT-LAP-0001 — Preventive — scheduled 2025-01-01",
        "fallback_answer": (
            "1 asset with overdue maintenance:\n"
            "• IT-LAP-0001 — Preventive (scheduled 2025-01-01)"
        ),
        "sources": [],
    }


@pytest.fixture(autouse=True)
def _clear_ollama_probe() -> None:
    reset_ollama_probe_cache()


def test_chat_ollama_offline_returns_tool_fallback() -> None:
    async def _run() -> None:
        service = AssistantService(MagicMock())
        tool_result = _overdue_tool_result()

        with patch.object(service, "_dispatch_tools", return_value=(tool_result, "get_overdue_maintenance")):
            with patch(
                "app.services.assistant_service.ollama_is_reachable",
                new_callable=AsyncMock,
                return_value=False,
            ):
                response = await service.chat(
                    AssistantChatRequest(message="What maintenance is overdue?", history=[]),
                )

        assert response.answer == tool_result["fallback_answer"]
        assert response.tools_used == ["get_overdue_maintenance"]

    asyncio.run(_run())


def test_chat_ollama_slow_returns_tool_fallback() -> None:
    async def _run() -> None:
        service = AssistantService(MagicMock())
        tool_result = _overdue_tool_result()

        with patch.object(service, "_dispatch_tools", return_value=(tool_result, "get_overdue_maintenance")):
            with patch(
                "app.services.assistant_service.ollama_is_reachable",
                new_callable=AsyncMock,
                return_value=True,
            ):
                with patch.object(
                    service,
                    "_ollama_format",
                    new_callable=AsyncMock,
                    side_effect=asyncio.TimeoutError,
                ):
                    response = await service.chat(
                        AssistantChatRequest(message="What maintenance is overdue?", history=[]),
                    )

        assert response.answer == tool_result["fallback_answer"]

    asyncio.run(_run())


def test_chat_ollama_success_returns_polished_answer() -> None:
    async def _run() -> None:
        service = AssistantService(MagicMock())
        tool_result = _overdue_tool_result()
        polished = "You have one overdue maintenance item: IT-LAP-0001 needs preventive service."

        with patch.object(service, "_dispatch_tools", return_value=(tool_result, "get_overdue_maintenance")):
            with patch(
                "app.services.assistant_service.ollama_is_reachable",
                new_callable=AsyncMock,
                return_value=True,
            ):
                with patch.object(
                    service,
                    "_ollama_format",
                    new_callable=AsyncMock,
                    return_value=polished,
                ):
                    response = await service.chat(
                        AssistantChatRequest(message="What maintenance is overdue?", history=[]),
                    )

        assert response.answer == polished
        assert "IT-LAP-0001" in response.answer

    asyncio.run(_run())


def test_chat_skip_ollama_tools_never_probe() -> None:
    async def _run() -> None:
        service = AssistantService(MagicMock())
        help_result = {
            "data_text": "Assistant capabilities",
            "fallback_answer": "I can help with fleet health, maintenance, and transfers.",
            "skip_ollama": True,
        }
        probe = AsyncMock(return_value=True)

        with patch.object(service, "_dispatch_tools", return_value=(help_result, "get_help")):
            with patch("app.services.assistant_service.ollama_is_reachable", probe):
                response = await service.chat(AssistantChatRequest(message="help", history=[]))

        probe.assert_not_called()
        assert response.answer == help_result["fallback_answer"]

    asyncio.run(_run())
