"""FastAPI app — the read-only dashboard backend.

Routes (all GET, all read-only):
- ``/healthz``        — liveness
- ``/api/overview``   — platform health stats, request series, backend panel
- ``/api/registry``   — registered models + task routing
- ``/api/leaderboard``— evaluation leaderboard (ranked)
- ``/api/adoption``   — usage / acceptance / impact
- ``/api/context``    — indexed-source inventory + retrieval preview

Mirrors the gateway's ``create_app(...)`` + ``app_factory()`` shape so the two
services read the same way.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard_api import data
from dashboard_api.schemas import (
    AdoptionPayload,
    ContextPayload,
    LeaderboardPayload,
    OverviewPayload,
    RegistryPayload,
)
from gateway.registry import Registry


def create_app(registry: Registry, sample_data: Path = data.DEFAULT_SAMPLE_DATA) -> FastAPI:
    from sovereign import __version__

    app = FastAPI(title="sovereign-dashboard-api", version=__version__)
    # Local dev: the Vite dev server (5173) calls this API (8090) cross-origin.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/overview")
    async def overview() -> OverviewPayload:
        return data.build_overview(registry)

    @app.get("/api/registry")
    async def registry_view() -> RegistryPayload:
        return data.build_registry(registry)

    @app.get("/api/leaderboard")
    async def leaderboard() -> LeaderboardPayload:
        return data.build_leaderboard()

    @app.get("/api/adoption")
    async def adoption() -> AdoptionPayload:
        return data.build_adoption()

    @app.get("/api/context")
    async def context() -> ContextPayload:
        return data.build_context(sample_data)

    return app


def app_factory() -> FastAPI:
    """Entry point for ``uvicorn dashboard_api.app:app_factory --factory``."""
    return create_app(data.load_default_registry())
