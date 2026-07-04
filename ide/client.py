"""Tiny gateway client for the CLI (keeps `ide` independent of other packages)."""

from __future__ import annotations


class GatewayClient:
    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def complete(self, prompt: str, task: str | None = None) -> str:
        import httpx

        headers = {"X-Sovereign-Task": task} if task else {}
        resp = httpx.post(
            f"{self._base_url}/v1/chat/completions",
            json={"model": task or "auto", "messages": [{"role": "user", "content": prompt}]},
            headers=headers,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        content: str = resp.json()["choices"][0]["message"]["content"]
        return content
