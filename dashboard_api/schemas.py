"""Typed response models — the contract the dashboard frontend consumes.

One model per view payload. Kept flat and presentation-shaped so the React
views can render straight from the JSON without client-side reshaping.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Stat(BaseModel):
    """A single stat tile: a label, a big value, and an optional trend delta."""

    label: str
    value: str
    delta: str | None = None
    tone: str = "neutral"  # "positive" | "neutral" — drives the delta colour


class Readiness(BaseModel):
    name: str
    status: str  # "healthy" | "degraded" | "down"


class BackendPanel(BaseModel):
    serving: str
    model: str
    quant: str
    readiness: list[Readiness]
    note: str | None = None


class OverviewPayload(BaseModel):
    stats: list[Stat]
    requests_series: list[float]
    backend: BackendPanel


class RegistryModel(BaseModel):
    name: str
    version: str
    quantization: str
    tasks: list[str]
    backend: str
    status: str  # "active" | "candidate"


class Route(BaseModel):
    task: str
    model: str
    backend: str


class RegistryPayload(BaseModel):
    models: list[RegistryModel]
    routing: list[Route]


class LeaderboardRow(BaseModel):
    name: str
    scores: dict[str, float]  # task -> pass rate (0..1)
    overall: float
    curated: bool = False
    measured: bool = False  # True when scores come from a real eval run (not fixtures)


class LeaderboardPayload(BaseModel):
    tasks: list[str]
    rows: list[LeaderboardRow]
    note: str | None = None


class SurfaceShare(BaseModel):
    label: str
    pct: int
    color: str  # token key: "indigo" | "emerald" | "sky"


class AdoptionPayload(BaseModel):
    stats: list[Stat]
    usage_series: list[float]
    by_surface: list[SurfaceShare]


class ContextSource(BaseModel):
    name: str
    path: str
    docs_label: str
    chunks: int
    icon: str  # token key the frontend maps to an SVG: "code"|"book"|"alert"|"layers"
    color: str  # "indigo" | "emerald" | "amber" | "violet"


class RetrievalHit(BaseModel):
    title: str
    path: str
    snippet: str
    score: float


class ContextPayload(BaseModel):
    total_chunks: int
    updated: str
    sources: list[ContextSource]
    query: str
    results: list[RetrievalHit] = Field(default_factory=list)
