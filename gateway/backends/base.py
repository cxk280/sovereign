"""Backend protocol — what the gateway needs from any serving engine.

Keeping this a narrow Protocol (one call to generate, one to health-check) means
Ollama, llama.cpp, and vLLM are drop-in interchangeable, and tests can inject a
fake with zero network. See design rule: depend on the abstraction, name the
concrete only at the composition root (``build_backends``).
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Backend(Protocol):
    name: str

    async def chat(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a chat completion for ``model`` and return the OpenAI-shaped JSON."""
        ...

    async def completions(self, model: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Run a (FIM) text completion — backs IDE autocomplete."""
        ...

    async def health(self) -> bool:
        """Return True if the backend is reachable and ready."""
        ...
