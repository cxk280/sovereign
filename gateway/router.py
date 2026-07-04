"""Task/model routing.

Resolution precedence for an incoming request:
1. an explicit **registered model name** wins;
2. otherwise a **task** (from the request's model field or the
   ``X-Sovereign-Task`` header) routes via ``routing.by_task``;
3. otherwise the registry ``default`` is used.
"""

from __future__ import annotations

from gateway.registry import ModelSpec, Registry


class ModelResolutionError(ValueError):
    """Raised when a request names a model or task the registry doesn't know."""


class Router:
    def __init__(self, registry: Registry) -> None:
        self._registry = registry

    def resolve(
        self, requested: str | None = None, task: str | None = None
    ) -> tuple[ModelSpec, str]:
        registry = self._registry
        resolved_task = task

        if requested and requested not in ("auto", "default"):
            spec = registry.get(requested)
            if spec is not None:
                return spec, resolved_task or _primary_task(spec)
            if requested in registry.routing.by_task:
                resolved_task = requested
            else:
                raise ModelResolutionError(f"unknown model or task: {requested!r}")

        if resolved_task and resolved_task in registry.routing.by_task:
            name = registry.routing.by_task[resolved_task]
        else:
            name = registry.routing.default

        spec = registry.get(name)
        if spec is None:
            raise ModelResolutionError(f"routing points to unregistered model: {name!r}")
        return spec, resolved_task or _primary_task(spec)


def _primary_task(spec: ModelSpec) -> str:
    return spec.tasks[0] if spec.tasks else "chat"
