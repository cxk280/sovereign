"""Illustrative fixtures — the numbers rendered in the approved Figma mocks.

Public-repo rule: synthetic/illustrative data only. These stand in where the
$0 local build has no live telemetry (a running fleet, an eval sweep, an
adoption pipeline). The registry and the context inventory are read from real
repo data in ``data.py``; everything here is clearly labelled illustrative in
the UI. Swap these for live sources when the platform is deployed.
"""

from __future__ import annotations

from typing import TypedDict


class StatDict(TypedDict):
    label: str
    value: str
    delta: str
    tone: str


class ReadinessDict(TypedDict):
    name: str
    status: str


class ModelDict(TypedDict):
    name: str
    version: str
    quantization: str
    tasks: list[str]
    backend: str
    status: str


class LeaderboardEntry(TypedDict):
    name: str
    scores: list[float]
    curated: bool


class SurfaceDict(TypedDict):
    label: str
    pct: int
    color: str


class HitDict(TypedDict):
    title: str
    path: str
    snippet: str
    score: float


class SourceMeta(TypedDict):
    name: str
    path: str
    docs_word: str
    chunks: int
    icon: str
    color: str


# --- Overview -----------------------------------------------------------------
OVERVIEW_STATS: list[StatDict] = [
    {"label": "MODELS LIVE", "value": "1", "delta": "1 candidate in eval", "tone": "neutral"},
    {"label": "REQUESTS / MIN", "value": "42", "delta": "▲ 12% vs last hr", "tone": "positive"},
    {"label": "P50 LATENCY", "value": "310 ms", "delta": "▼ 18 ms", "tone": "positive"},
    {"label": "P95 LATENCY", "value": "680 ms", "delta": "▼ 40 ms", "tone": "positive"},
    {"label": "TOKENS / SEC", "value": "95", "delta": "▲ 6%", "tone": "positive"},
    {"label": "ERROR RATE", "value": "0.4%", "delta": "▼ 0.1%", "tone": "positive"},
]
# requests/min sampled over the last hour (24 x 2.5-min buckets)
OVERVIEW_REQUESTS_SERIES: list[int] = [
    22, 26, 24, 30, 28, 34, 31, 38, 36, 33, 40, 44,
    41, 47, 43, 50, 46, 52, 48, 45, 42, 49, 44, 42,
]
OVERVIEW_READINESS: list[ReadinessDict] = [
    {"name": "Gateway", "status": "healthy"},
    {"name": "Qdrant (RAG)", "status": "healthy"},
    {"name": "Model loaded", "status": "healthy"},
]

# --- Registry: candidate models beyond the active local one -------------------
# The active model comes from gateway/registry.yaml; these are the eval
# candidates the leaderboard scores.
CANDIDATE_MODELS: list[ModelDict] = [
    {
        "name": "qwen2.5-coder:7b",
        "version": "7b-instruct",
        "quantization": "Q4_K_M",
        "tasks": ["code-gen", "code-review", "test-gen"],
        "backend": "vLLM · A16",
        "status": "candidate",
    },
    {
        "name": "deepseek-coder:6.7b",
        "version": "6.7b-instruct",
        "quantization": "Q4_K_M",
        "tasks": ["code-gen", "test-gen"],
        "backend": "vLLM · A16",
        "status": "candidate",
    },
    {
        "name": "llama-3.2:3b",
        "version": "3b-instruct",
        "quantization": "Q5_K_M",
        "tasks": ["chat", "code-review"],
        "backend": "Ollama · local",
        "status": "candidate",
    },
    {
        "name": "mistral:7b",
        "version": "7b-instruct",
        "quantization": "Q4_K_M",
        "tasks": ["chat"],
        "backend": "vLLM · A16",
        "status": "candidate",
    },
]

# --- Leaderboard (matches docs/assets/leaderboard-sample.png) ------------------
LEADERBOARD_TASKS: list[str] = ["code-gen", "code-review", "test-gen"]
LEADERBOARD: list[LeaderboardEntry] = [
    {"name": "qwen2.5-coder:7b", "scores": [0.92, 0.78, 0.85], "curated": True},
    {"name": "deepseek-coder:6.7b", "scores": [0.88, 0.72, 0.80], "curated": False},
    {"name": "llama-3.2:3b", "scores": [0.70, 0.66, 0.68], "curated": False},
    {"name": "mistral:7b", "scores": [0.74, 0.60, 0.66], "curated": False},
]
LEADERBOARD_NOTE = (
    "Deployed locally as qwen2.5-coder:1.5b (Q4_K_M) — the same family at a "
    "laptop-sized quant. Benchmarked against a Vultr A16."
)

# --- Adoption -----------------------------------------------------------------
ADOPTION_STATS: list[StatDict] = [
    {"label": "TOTAL REQUESTS · 30d", "value": "18,420", "delta": "▲ 23% MoM", "tone": "positive"},
    {"label": "ACCEPTANCE RATE", "value": "71%", "delta": "▲ 4 pts", "tone": "positive"},
    {"label": "EST. HOURS SAVED", "value": "96 h", "delta": "▲ 18 h", "tone": "positive"},
    {"label": "ACTIVE DEVELOPERS", "value": "14", "delta": "▲ 2 this month", "tone": "positive"},
]
ADOPTION_USAGE_SERIES: list[int] = [
    380, 420, 410, 300, 290, 460, 510, 480, 520, 505,
    360, 340, 560, 590, 570, 610, 640, 430, 410, 660,
    680, 700, 720, 690, 470, 450, 730, 760, 780, 742,
]
ADOPTION_BY_SURFACE: list[SurfaceDict] = [
    {"label": "IDE — Continue / Cursor", "pct": 58, "color": "indigo"},
    {"label": "CI — GitLab pipelines", "pct": 27, "color": "emerald"},
    {"label": "CLI — sov", "pct": 15, "color": "sky"},
]

# --- Context: retrieval preview (grounded in real sample_data/ paths) ---------
CONTEXT_QUERY = "How do we roll back a bad deploy?"
CONTEXT_RESULTS: list[HitDict] = [
    {
        "title": "Deploy rollback",
        "path": "runbooks/deploy-rollback.md",
        "snippet": (
            "Re-point the router to the previous model in registry.yaml, then "
            "redeploy the gateway — routing is a single-field revert."
        ),
        "score": 0.90,
    },
    {
        "title": "INC-2025-001 — orders latency spike",
        "path": "incidents/INC-2025-001-orders-latency-spike.md",
        "snippet": (
            "Mitigated by rolling back the orders-api deploy; p95 recovered "
            "within 4 minutes of the revert."
        ),
        "score": 0.83,
    },
    {
        "title": "ADR-0002 — Postgres as system of record",
        "path": "architecture/ADR-0002-postgres-as-system-of-record.md",
        "snippet": (
            "Migrations are backward-compatible, so a rollback never strands "
            "in-flight writes."
        ),
        "score": 0.71,
    },
]

# Per-source presentation metadata for the context inventory. Doc counts are read
# from sample_data/ at runtime; chunk estimates are illustrative.
CONTEXT_SOURCE_META: dict[str, SourceMeta] = {
    "services": {
        "name": "Codebase",
        "path": "services/orders-api",
        "docs_word": "files",
        "chunks": 48,
        "icon": "code",
        "color": "indigo",
    },
    "runbooks": {
        "name": "Runbooks",
        "path": "runbooks/",
        "docs_word": "docs",
        "chunks": 36,
        "icon": "book",
        "color": "emerald",
    },
    "incidents": {
        "name": "Incidents",
        "path": "incidents/",
        "docs_word": "records",
        "chunks": 24,
        "icon": "alert",
        "color": "amber",
    },
    "architecture": {
        "name": "Architecture",
        "path": "architecture/",
        "docs_word": "docs",
        "chunks": 30,
        "icon": "layers",
        "color": "violet",
    },
}
