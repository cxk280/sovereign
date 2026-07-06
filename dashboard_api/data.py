"""Assemble each view's payload from real repo data + illustrative fixtures.

Real sources: ``gateway/registry.yaml`` (registry + routing + models-live) and
``sample_data/`` (context inventory doc counts). Everything else is drawn from
``fixtures`` and clearly labelled illustrative in the UI.
"""

from __future__ import annotations

from pathlib import Path

from dashboard_api import fixtures as fx
from dashboard_api.results import BenchMeasurement, load_eval_results
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


# Honest provenance labels for a measured run, keyed by the bench.meta.json "host".
# The serving pill and note are driven by *where the numbers were actually measured*
# — never inferred — so CPU numbers can never be shown as A16 GPU numbers. A host of
# "local"/unknown/absent falls through to the generic measured note below.
_MEASURED_HOST: dict[str, tuple[str, str]] = {
    "vultr-cpu": ("Ollama · Vultr CPU", "Latency & tokens/sec measured on Vultr CPU compute"),
    "vultr-a16": ("vLLM · Vultr A16", "Latency & tokens/sec measured on Vultr A16"),
}


def _fmt_latency(seconds: float) -> str:
    return f"{seconds * 1000:.0f} ms" if seconds < 1 else f"{seconds:.2f} s"


def _apply_measured_perf(stats: list[Stat], m: BenchMeasurement) -> None:
    """Override the latency + tokens/sec tiles in place with measured values."""
    for s in stats:
        if s.label == "TOKENS / SEC":
            s.value = f"{m.tokens_per_s:.0f}"
            s.delta, s.tone = "measured", "neutral"
        elif s.label == "P50 LATENCY":
            s.label = "AVG LATENCY"  # bench.json measures average request latency, not p50
            s.value = _fmt_latency(m.avg_latency_s)
            s.delta, s.tone = "measured", "neutral"


def build_overview(registry: Registry, results_dir: Path | None = None) -> OverviewPayload:
    stats = [Stat(**s) for s in fx.OVERVIEW_STATS]
    stats[0].value = str(len(registry.models))  # models-live is real
    active = registry.models[0] if registry.models else None

    note = "vLLM · Vultr A16 available for benchmark runs"
    serving = _backend_label(active.backend) if active else _LOCAL_BACKEND_LABEL
    results = load_eval_results(results_dir)
    if results.has_bench:
        _apply_measured_perf(stats, results.bench[0])
        # Label from provenance only: a known measured host sets both the serving
        # pill and the note; anything else stays honest-but-generic.
        measured = _MEASURED_HOST.get(results.host or "")
        if measured:
            serving, note = measured
        else:
            note = "Latency & tokens/sec measured from a real eval run"

    backend = BackendPanel(
        serving=serving,
        model=active.name if active else "—",
        quant=(active.quantization or "—") if active else "—",
        readiness=[Readiness(**r) for r in fx.OVERVIEW_READINESS],
        note=note,
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


def _merge_measured_leaderboard(
    rows: list[LeaderboardRow], tasks: list[str], measured: dict[str, dict[str, float]]
) -> list[LeaderboardRow]:
    """Overlay measured rows: replace a fixture row of the same model, else append."""
    by_name = {r.name: r for r in rows}
    for model, scores in measured.items():
        task_scores = {t: float(scores.get(t, 0.0)) for t in tasks}
        overall = scores.get("overall")
        if overall is None:
            overall = sum(task_scores.values()) / len(tasks) if tasks else 0.0
        by_name[model] = LeaderboardRow(
            name=model,
            scores=task_scores,
            overall=round(float(overall), 4),
            curated=by_name[model].curated if model in by_name else False,
            measured=True,
        )
    return list(by_name.values())


def build_leaderboard(results_dir: Path | None = None) -> LeaderboardPayload:
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

    note = fx.LEADERBOARD_NOTE
    results = load_eval_results(results_dir)
    if results.has_leaderboard:
        rows = _merge_measured_leaderboard(rows, tasks, results.leaderboard)
        note = f"{fx.LEADERBOARD_NOTE} Rows marked measured come from a real eval run."

    rows.sort(key=lambda r: r.overall, reverse=True)
    return LeaderboardPayload(tasks=tasks, rows=rows, note=note)


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
