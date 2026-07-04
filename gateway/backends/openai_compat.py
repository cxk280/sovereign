"""A generic OpenAI-compatible HTTP backend.

Ollama, llama.cpp's server, and vLLM all expose ``/v1/chat/completions``, so a
single client covers every serving engine — only the base URL, auth, and health
path differ. This is what makes the local ($0) and Vultr-GPU (vLLM) paths
swappable behind one gateway.
"""

from __future__ import annotations

from typing import Any

import httpx


class OpenAICompatBackend:
    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str | None = None,
        health_path: str = "/health",
        timeout: float = 120.0,
    ) -> None:
        self.name = name
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._health_path = health_path
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"} if self._api_key else {}

    async def _post(self, path: str, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = {**payload, "model": model, "stream": False}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(f"{self._base_url}{path}", json=body, headers=self._headers())
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
            return data

    async def chat(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/v1/chat/completions", model, payload)

    async def completions(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._post("/v1/completions", model, payload)

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self._base_url}{self._health_path}", headers=self._headers()
                )
                return resp.status_code == 200
        except httpx.HTTPError:
            return False
