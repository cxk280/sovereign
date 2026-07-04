"""FastAPI app — the OpenAI-compatible gateway.

Routes:
- ``GET  /healthz`` / ``GET /readyz`` — liveness / readiness (reliability)
- ``GET  /metrics``                   — Prometheus scrape
- ``GET  /v1/models``                 — registry, in OpenAI list shape
- ``POST /v1/chat/completions``       — resolve → proxy → record metrics
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from gateway.backends.base import Backend
from gateway.backends.openai_compat import OpenAICompatBackend
from gateway.config import Settings, load_settings
from gateway.metrics import LATENCY, REQUESTS, TOKENS
from gateway.registry import Registry, load_registry
from gateway.router import ModelResolutionError, Router
from gateway.schemas import ChatCompletionRequest


def build_backends(settings: Settings) -> dict[str, Backend]:
    """Composition root — the one place concrete backends are named."""
    backends: dict[str, Backend] = {
        "ollama": OpenAICompatBackend(
            "ollama", settings.backends.ollama_base_url, health_path="/api/tags"
        ),
        "llamacpp": OpenAICompatBackend(
            "llamacpp", settings.backends.llamacpp_base_url, health_path="/health"
        ),
    }
    if settings.backends.vllm_base_url:  # production: vLLM on Vultr Cloud GPU
        backends["vllm"] = OpenAICompatBackend(
            "vllm",
            settings.backends.vllm_base_url,
            api_key=settings.backends.vllm_api_key,
            health_path="/health",
        )
    return backends


def create_app(registry: Registry, backends: dict[str, Backend]) -> FastAPI:
    from sovereign import __version__

    app = FastAPI(title="sovereign-gateway", version=__version__)
    router = Router(registry)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    async def readyz() -> JSONResponse:
        results = {name: await b.health() for name, b in backends.items()}
        ready = any(results.values())
        return JSONResponse(
            {"ready": ready, "backends": results}, status_code=200 if ready else 503
        )

    @app.get("/metrics")
    async def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/v1/models")
    async def list_models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": m.name,
                    "object": "model",
                    "owned_by": "sovereign",
                    "sovereign": {
                        "version": m.version,
                        "quantization": m.quantization,
                        "backend": m.backend,
                        "tasks": m.tasks,
                    },
                }
                for m in registry.models
            ],
        }

    @app.post("/v1/chat/completions")
    async def chat_completions(req: ChatCompletionRequest, request: Request) -> dict[str, Any]:
        task_hint = request.headers.get("x-sovereign-task")
        try:
            spec, task = router.resolve(req.model, task_hint)
        except ModelResolutionError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        backend = backends.get(spec.backend)
        if backend is None:
            raise HTTPException(status_code=503, detail=f"backend {spec.backend!r} not available")

        payload = req.model_dump(exclude_none=True)
        payload.pop("model", None)

        start = time.perf_counter()
        try:
            result = await backend.chat(spec.name, payload)
        except Exception as exc:  # backend/network failure → 502, recorded
            REQUESTS.labels(spec.name, task, "error").inc()
            raise HTTPException(status_code=502, detail=f"backend error: {exc}") from exc

        LATENCY.labels(spec.name).observe(time.perf_counter() - start)
        REQUESTS.labels(spec.name, task, "ok").inc()
        usage = result.get("usage")
        if isinstance(usage, dict):
            TOKENS.labels(spec.name, "prompt").inc(usage.get("prompt_tokens") or 0)
            TOKENS.labels(spec.name, "completion").inc(usage.get("completion_tokens") or 0)
        return result

    return app


def app_factory() -> FastAPI:
    """Entry point for ``uvicorn gateway.app:app_factory --factory``."""
    settings = load_settings()
    registry = load_registry(settings.registry_path)
    return create_app(registry, build_backends(settings))
