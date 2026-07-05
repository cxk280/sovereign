"""Run the full suite: every client against every task, timed."""

from __future__ import annotations

import time
from dataclasses import dataclass

from eval.client import ModelClient
from eval.scorers import score_codegen, score_review, score_testgen
from eval.tasks import load_codegen, load_review, load_testgen

CODEGEN = "code-gen"
REVIEW = "code-review"
TESTGEN = "test-gen"


@dataclass
class Result:
    model: str
    task_type: str
    task_id: str
    passed: bool
    latency_s: float


def _timed(client: ModelClient, prompt: str) -> tuple[str, float]:
    start = time.perf_counter()
    try:
        out = client.complete(prompt)
    except Exception:
        # A single failed/timed-out call scores as a miss instead of crashing the
        # whole suite — one flaky request must not throw away a paid benchmark run.
        out = ""
    return out, time.perf_counter() - start


def run_suite(clients: list[ModelClient]) -> list[Result]:
    codegen, review, testgen = load_codegen(), load_review(), load_testgen()
    results: list[Result] = []
    for c in clients:
        for t in codegen:
            out, dt = _timed(c, t.prompt)
            results.append(Result(c.name, CODEGEN, t.id, score_codegen(t, out), dt))
        for r in review:
            out, dt = _timed(c, f"Review this code and name any bug:\n\n{r.diff}")
            results.append(Result(c.name, REVIEW, r.id, score_review(r, out), dt))
        for g in testgen:
            out, dt = _timed(c, g.prompt)
            results.append(Result(c.name, TESTGEN, g.id, score_testgen(g, out), dt))
    return results
