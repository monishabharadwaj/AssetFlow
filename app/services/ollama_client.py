from __future__ import annotations

import httpx

from app.core.config import settings


async def ollama_generate(prompt: str, *, timeout: float | None = None) -> str:
    timeout_seconds = timeout if timeout is not None else settings.ollama_timeout_seconds
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
            },
        )
        response.raise_for_status()
        payload = response.json()
        return (payload.get("response") or "").strip()
