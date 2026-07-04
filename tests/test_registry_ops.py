"""Curation writes eval winners into the registry; promote/rollback move the default."""

import yaml

from eval.registry_ops import best_model_per_task, curate_registry, promote, rollback

_REGISTRY = {
    "models": [
        {"name": "alpha", "version": "1", "backend": "ollama", "tasks": ["code-gen"]},
        {"name": "beta", "version": "1", "backend": "ollama", "tasks": ["code-review"]},
    ],
    "routing": {"default": "alpha", "by_task": {"code-gen": "alpha", "code-review": "alpha"}},
}


def _write(tmp_path):
    p = tmp_path / "registry.yaml"
    p.write_text(yaml.safe_dump(_REGISTRY, sort_keys=False))
    return p


def test_best_model_per_task() -> None:
    lb = {
        "alpha": {"code-gen": 0.9, "code-review": 0.2, "overall": 0.55},
        "beta": {"code-gen": 0.3, "code-review": 0.8, "overall": 0.55},
    }
    assert best_model_per_task(lb) == {"code-gen": "alpha", "code-review": "beta"}


def test_curate_registry_routes_task_to_best_registered_model(tmp_path) -> None:
    p = _write(tmp_path)
    lb = {
        "alpha": {"code-gen": 0.9, "code-review": 0.2, "overall": 0.55},
        "beta": {"code-gen": 0.3, "code-review": 0.8, "overall": 0.55},
    }
    applied = curate_registry(p, lb)
    assert applied["code-review"] == "beta"
    data = yaml.safe_load(p.read_text())
    assert data["routing"]["by_task"]["code-review"] == "beta"


def test_promote_and_rollback(tmp_path) -> None:
    p = _write(tmp_path)
    previous = promote(p, "beta")
    assert previous == "alpha"
    assert yaml.safe_load(p.read_text())["routing"]["default"] == "beta"
    rollback(p, previous)
    assert yaml.safe_load(p.read_text())["routing"]["default"] == "alpha"
