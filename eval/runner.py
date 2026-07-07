"""Run the full suite: every client against every task, timed."""

from __future__ import annotations

import time
from dataclasses import dataclass

from eval.client import ModelClient
from eval.scorers import (
    judge_review_with_model,
    score_codegen,
    score_review,
    score_testgen,
)
from eval.tasks import ReviewTask, load_codegen, load_review, load_testgen

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


def _score_review(task: ReviewTask, output: str, judge: ModelClient | None) -> bool:
    """Prefer the LLM-as-judge when one is supplied (asks "did the review find the real
    bug?"); the substring keyword scorer is the fallback. A flaky/unreachable judge falls
    back to keywords for that item rather than zeroing out the whole review category."""
    if judge is None:
        return score_review(task, output)
    try:
        return judge_review_with_model(task, output, judge)
    except Exception:
        return score_review(task, output)


def run_suite(
    clients: list[ModelClient],
    *,
    samples: int = 1,
    judge: ModelClient | None = None,
) -> list[Result]:
    """Run every client against every task, timed.

    ``samples`` generations per task reduce variance: each (model, task) is run N times
    and each run is emitted as its own ``Result``, so the leaderboard's ``passed/total``
    aggregation turns into a fractional pass rate for free — no change downstream. When a
    ``judge`` client is given, code-review is scored by the LLM-as-judge (see
    ``_score_review``); otherwise the keyword scorer is used.
    """
    codegen, review, testgen = load_codegen(), load_review(), load_testgen()
    results: list[Result] = []
    for c in clients:
        for _ in range(samples):
            for t in codegen:
                out, dt = _timed(c, t.prompt)
                results.append(Result(c.name, CODEGEN, t.id, score_codegen(t, out), dt))
            for r in review:
                out, dt = _timed(c, f"Review this code and name any bug:\n\n{r.diff}")
                results.append(Result(c.name, REVIEW, r.id, _score_review(r, out, judge), dt))
            for g in testgen:
                out, dt = _timed(c, g.prompt)
                results.append(Result(c.name, TESTGEN, g.id, score_testgen(g, out), dt))
    return results
