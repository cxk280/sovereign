"""Aggregate raw results into a leaderboard (per-task pass rate + overall)."""

from __future__ import annotations

from collections import defaultdict

from eval.runner import Result

Leaderboard = dict[str, dict[str, float]]


def build_leaderboard(results: list[Result]) -> Leaderboard:
    total: dict[tuple[str, str], int] = defaultdict(int)
    passed: dict[tuple[str, str], int] = defaultdict(int)
    for r in results:
        total[(r.model, r.task_type)] += 1
        passed[(r.model, r.task_type)] += int(r.passed)

    models = sorted({r.model for r in results})
    tasks = sorted({r.task_type for r in results})
    lb: Leaderboard = {}
    for m in models:
        scores = {t: (passed[(m, t)] / total[(m, t)] if total[(m, t)] else 0.0) for t in tasks}
        scores["overall"] = sum(scores.values()) / len(tasks) if tasks else 0.0
        lb[m] = scores
    return lb


def to_markdown(lb: Leaderboard) -> str:
    if not lb:
        return "_No results._"
    tasks = [t for t in next(iter(lb.values())) if t != "overall"] + ["overall"]
    header = "| Model | " + " | ".join(tasks) + " |"
    sep = "|" + "---|" * (len(tasks) + 1)
    ranked = sorted(lb.items(), key=lambda kv: kv[1]["overall"], reverse=True)
    rows = ["| " + m + " | " + " | ".join(f"{s[t]:.0%}" for t in tasks) + " |" for m, s in ranked]
    return "\n".join([header, sep, *rows])
