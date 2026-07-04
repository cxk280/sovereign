"""Registry loads and matches the shipped routing config."""

from gateway.registry import load_registry


def test_registry_loads_and_has_default_route() -> None:
    reg = load_registry("gateway/registry.yaml")
    assert reg.models, "registry must define at least one model"
    default = reg.get(reg.routing.default)
    assert default is not None, "default route must point to a registered model"


def test_every_task_route_points_to_a_registered_model() -> None:
    reg = load_registry("gateway/registry.yaml")
    for task, name in reg.routing.by_task.items():
        assert reg.get(name) is not None, f"task {task!r} routes to unknown model {name!r}"
