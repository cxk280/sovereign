"""Curation + lifecycle: turn eval evidence into gateway registry changes.

- **curate_registry** — the "curate" half of "evaluate and curate": route each
  task to its best-scoring *registered* model.
- **promote / rollback** — model lifecycle: switch the default route to a model
  (returning the previous default so the caller can roll back).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from eval.leaderboard import Leaderboard


def _load(path: str | Path) -> dict:
    return yaml.safe_load(Path(path).read_text())


def _save(path: str | Path, data: dict) -> None:
    Path(path).write_text(yaml.safe_dump(data, sort_keys=False))


def best_model_per_task(lb: Leaderboard) -> dict[str, str]:
    tasks = [t for t in next(iter(lb.values())) if t != "overall"]
    return {t: max(lb, key=lambda m: lb[m][t]) for t in tasks}


def curate_registry(registry_path: str | Path, lb: Leaderboard) -> dict[str, str]:
    """Point each task's route at its best *registered* model. Returns applied routes."""
    data = _load(registry_path)
    registered = {m["name"] for m in data["models"]}
    applied: dict[str, str] = {}
    for task, model in best_model_per_task(lb).items():
        if model in registered and task in data["routing"]["by_task"]:
            data["routing"]["by_task"][task] = model
            applied[task] = model
    _save(registry_path, data)
    return applied


def promote(registry_path: str | Path, name: str) -> str:
    """Make ``name`` the default route. Returns the previous default (for rollback)."""
    data = _load(registry_path)
    if name not in {m["name"] for m in data["models"]}:
        raise ValueError(f"model not registered: {name!r}")
    previous = data["routing"]["default"]
    data["routing"]["default"] = name
    _save(registry_path, data)
    return previous


def rollback(registry_path: str | Path, previous: str) -> None:
    promote(registry_path, previous)
