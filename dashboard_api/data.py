"""Assemble each view's payload from real repo data + illustrative fixtures.

Real sources: ``gateway/registry.yaml`` (registry + routing + models-live) and
``sample_data/`` (context inventory doc counts). Everything else is drawn from
``fixtures`` and clearly labelled illustrative in the UI.
"""

from __future__ import annotations

from pathlib import Path

from dashboard_api import fixtures as fx
from dashboard_api.schemas import (
    AdoptionPayload,
    BackendPanel,
    ContextPayload,
    ContextSource,
    LeaderboardPayload,
    LeaderboardRow,
    OverviewPayload,
    Readiness,
    RegistryModel,
    RegistryPayload,
    RetrievalHit,
    Route,
    Stat,
    SurfaceShare,
)
from gateway.registry import Registry, load_registry

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_PATH = REPO_ROOT / "gateway" / "registry.yaml"
DEFAULT_SAMPLE_DATA = REPO_ROOT / "sample_data"

# A friendly backend label for the local active model.
_LOCAL_BACKEND_LABEL = "Ollama · local"


def _backend_label(backend: str) -> str:
    return {"ollama": _LOCAL_BACKEND_LABEL, "vllm": "vLLM · Vultr A16"}.get(backend, backend)


def build_overview(registry: Registry) -> OverviewPayload:
    stats = [Stat(**s) for s in fx.OVERVIEW_STATS]
    stats[0].value = str(len(registry.models))  # models-live is real
    active = registry.models[0] if registry.models else None
    backend = BackendPanel(
        serving=_backend_label(active.backend) if active else _LOCAL_BACKEND_LABEL,
        model=active.name if active else "—",
        quant=(active.quantization or "—") if active else "—",
        readiness=[Readiness(**r) for r in fx.OVERVIEW_READINESS],
        note="vLLM · Vultr A16 available for benchmark runs",
    )
    return OverviewPayload(
        stats=stats,
        requests_series=[float(v) for v in fx.OVERVIEW_REQUESTS_SERIES],
        backend=backend,
    )


def build_registry(registry: Registry) -> RegistryPayload:
    # Active models are real (from registry.yaml); candidates are eval fixtures.
    active = [
        RegistryModel(
            name=m.name,
            version=m.version,
            quantization=m.quantization or "—",
            tasks=m.tasks,
            backend=_backend_label(m.backend),
            status="active",
        )
        for m in registry.models
    ]
    candidates = [RegistryModel(**c) for c in fx.CANDIDATE_MODELS]
    routing = [
        Route(
            task=task,
            model=model,
            backend=_backend_label(_route_backend(registry, model)),
        )
        for task, model in registry.routing.by_task.items()
    ]
    return RegistryPayload(models=active + candidates, routing=routing)


def _route_backend(registry: Registry, model: str) -> str:
    spec = registry.get(model)
    return spec.backend if spec else "ollama"


def build_leaderboard() -> LeaderboardPayload:
    tasks = fx.LEADERBOARD_TASKS
    rows = []
    for entry in fx.LEADERBOARD:
        scores = dict(zip(tasks, entry["scores"], strict=True))
        overall = sum(scores.values()) / len(scores)
        rows.append(
            LeaderboardRow(
                name=entry["name"],
                scores=scores,
                overall=round(overall, 4),
                curated=entry["curated"],
            )
        )
    rows.sort(key=lambda r: r.overall, reverse=True)
    return LeaderboardPayload(tasks=tasks, rows=rows, note=fx.LEADERBOARD_NOTE)


def build_adoption() -> AdoptionPayload:
    return AdoptionPayload(
        stats=[Stat(**s) for s in fx.ADOPTION_STATS],
        usage_series=[float(v) for v in fx.ADOPTION_USAGE_SERIES],
        by_surface=[SurfaceShare(**s) for s in fx.ADOPTION_BY_SURFACE],
    )


def _count_docs(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for p in directory.rglob("*") if p.is_file() and not p.name.startswith("."))


def build_context(sample_data: Path = DEFAULT_SAMPLE_DATA) -> ContextPayload:
    sources: list[ContextSource] = []
    total_chunks = 0
    for key, meta in fx.CONTEXT_SOURCE_META.items():
        docs = _count_docs(sample_data / key)
        total_chunks += int(meta["chunks"])
        sources.append(
            ContextSource(
                name=str(meta["name"]),
                path=str(meta["path"]),
                docs_label=f"{docs} {meta['docs_word']}",
                chunks=int(meta["chunks"]),
                icon=str(meta["icon"]),
                color=str(meta["color"]),
            )
        )
    return ContextPayload(
        total_chunks=total_chunks,
        updated="2h ago",
        sources=sources,
        query=fx.CONTEXT_QUERY,
        results=[RetrievalHit(**r) for r in fx.CONTEXT_RESULTS],
    )


def load_default_registry(path: str | Path = DEFAULT_REGISTRY_PATH) -> Registry:
    return load_registry(path)
