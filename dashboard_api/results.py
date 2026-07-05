"""Load measured eval artifacts (``eval/results/``) when a benchmark has run.

The eval harness writes ``bench.json`` (latency + tokens/sec) and
``leaderboard.json`` (pass rates) from a real run — e.g. the Vultr A16 GPU
benchmark. When those files exist the dashboard shows the **measured** numbers;
when they are absent or malformed it falls back to the illustrative fixtures, so
local ($0) dev and CI stay green either way. This module never raises: any read
or parse problem degrades to "no measured data" and the caller uses fixtures.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS_DIR = REPO_ROOT / "eval" / "results"


@dataclass(frozen=True)
class BenchMeasurement:
    """One row of ``bench.json`` — measured latency/throughput for a model."""

    model: str
    requests: int
    avg_latency_s: float
    tokens_per_s: float


@dataclass(frozen=True)
class EvalResults:
    """Parsed measured artifacts; empty containers mean "fall back to fixtures"."""

    bench: list[BenchMeasurement]
    leaderboard: dict[str, dict[str, float]]  # model -> {task: rate, "overall": rate}

    @property
    def has_bench(self) -> bool:
        return bool(self.bench)

    @property
    def has_leaderboard(self) -> bool:
        return bool(self.leaderboard)


def _resolve_dir(results_dir: Path | None) -> Path:
    if results_dir is not None:
        return results_dir
    env = os.getenv("SOVEREIGN_EVAL_RESULTS")
    return Path(env) if env else DEFAULT_RESULTS_DIR


def _read_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def _parse_bench(raw: object | None) -> list[BenchMeasurement]:
    if not isinstance(raw, list):
        return []
    out: list[BenchMeasurement] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        try:
            out.append(
                BenchMeasurement(
                    model=str(item["model"]),
                    requests=int(item["requests"]),
                    avg_latency_s=float(item["avg_latency_s"]),
                    tokens_per_s=float(item["tokens_per_s"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue  # skip a malformed row, keep the rest
    return out


def _parse_leaderboard(raw: object | None) -> dict[str, dict[str, float]]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, dict[str, float]] = {}
    for model, scores in raw.items():
        if not isinstance(scores, dict):
            continue
        clean: dict[str, float] = {}
        for task, rate in scores.items():
            try:
                clean[str(task)] = float(rate)
            except (TypeError, ValueError):
                continue
        if clean:
            out[str(model)] = clean
    return out


def load_eval_results(results_dir: Path | None = None) -> EvalResults:
    """Read measured artifacts from ``results_dir`` (or env / default). Never raises."""
    d = _resolve_dir(results_dir)
    return EvalResults(
        bench=_parse_bench(_read_json(d / "bench.json")),
        leaderboard=_parse_leaderboard(_read_json(d / "leaderboard.json")),
    )
