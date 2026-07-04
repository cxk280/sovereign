"""Router resolution precedence: explicit model > task > default."""

import pytest

from gateway.registry import ModelSpec, Registry, RoutingConfig
from gateway.router import ModelResolutionError, Router


def _registry() -> Registry:
    return Registry(
        models=[
            ModelSpec(name="coder", version="1", backend="ollama", tasks=["code-gen", "chat"]),
            ModelSpec(name="reviewer", version="1", backend="ollama", tasks=["code-review"]),
        ],
        routing=RoutingConfig(
            default="coder",
            by_task={"code-gen": "coder", "code-review": "reviewer"},
        ),
    )


def test_explicit_model_wins() -> None:
    spec, _ = Router(_registry()).resolve("reviewer", task="code-gen")
    assert spec.name == "reviewer"


def test_task_routes_when_model_is_auto() -> None:
    spec, task = Router(_registry()).resolve("auto", task="code-review")
    assert spec.name == "reviewer"
    assert task == "code-review"


def test_model_field_as_task_alias() -> None:
    spec, task = Router(_registry()).resolve("code-review")
    assert spec.name == "reviewer"
    assert task == "code-review"


def test_default_when_nothing_specified() -> None:
    spec, _ = Router(_registry()).resolve()
    assert spec.name == "coder"


def test_unknown_model_or_task_raises() -> None:
    with pytest.raises(ModelResolutionError):
        Router(_registry()).resolve("does-not-exist")
