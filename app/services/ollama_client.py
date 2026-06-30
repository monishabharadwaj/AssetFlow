from __future__ import annotations

import time

import httpx

from app.core.config import settings

_PROBE_TTL_SECONDS = 5.0
_reachable: bool | None = None
_checked_at: float = 0.0


def reset_ollama_probe_cache() -> None:
    """Clear cached reachability (for tests)."""
    global _reachable, _checked_at
    _reachable = None
    _checked_at = 0.0


async def ollama_is_reachable(*, probe_timeout: float = 2.0) -> bool:
    """Fast probe so offline Ollama skips generate without a long hang."""
    global _reachable, _checked_at
    now = time.monotonic()
    if _reachable is not None and now - _checked_at < _PROBE_TTL_SECONDS:
        return _reachable
    try:
        async with httpx.AsyncClient(timeout=probe_timeout) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            _reachable = response.is_success
    except Exception:
        _reachable = False
    _checked_at = now
    return _reachable


async def ollama_generate(
    prompt: str,
    *,
    timeout: float | None = None,
    temperature: float = 0.3,
    num_predict: int = 256,
) -> str:
    timeout_seconds = timeout if timeout is not None else settings.ollama_timeout_seconds
    async with httpx.AsyncClient(timeout=timeout_seconds) as client:
        response = await client.post(
            f"{settings.ollama_base_url}/api/generate",
            json={
                "model": settings.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": num_predict},
            },
        )
        response.raise_for_status()
        payload = response.json()
        return (payload.get("response") or "").strip()
