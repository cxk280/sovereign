"""Model clients — how the harness talks to a model.

``GatewayClient`` calls the sovereign gateway's OpenAI-compatible endpoint, so any
served/registered model is evaluable. ``StubClient`` is a deterministic in-process
fake for tests (a callable maps prompt -> completion), so the whole pipeline runs
offline with no network.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, runtime_checkable


@runtime_checkable
class ModelClient(Protocol):
    name: str

    def complete(self, prompt: str, system: str | None = None) -> str: ...


class StubClient:
    def __init__(self, name: str, handler: Callable[[str], str]) -> None:
        self.name = name
        self._handler = handler

    def complete(self, prompt: str, system: str | None = None) -> str:
        return self._handler(prompt)


class GatewayClient:
    def __init__(self, base_url: str, model: str, timeout: float = 120.0) -> None:
        self.name = model
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    def complete(self, prompt: str, system: str | None = None) -> str:
        import httpx

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = httpx.post(
            f"{self._base_url}/v1/chat/completions",
            json={"model": self._model, "messages": messages},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        content: str = resp.json()["choices"][0]["message"]["content"]
        return content
