"""Model registry — the source of truth for lifecycle management.

Each ``ModelSpec`` records a model's version, quantization, serving backend, and
the tasks it is approved for. ``RoutingConfig`` maps tasks to models. This is the
data the dashboard's registry view and the router both read.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ModelSpec(BaseModel):
    name: str
    version: str
    backend: str
    quantization: str | None = None
    tasks: list[str] = Field(default_factory=list)
    context_length: int | None = None


class RoutingConfig(BaseModel):
    default: str
    by_task: dict[str, str] = Field(default_factory=dict)


class Registry(BaseModel):
    models: list[ModelSpec]
    routing: RoutingConfig

    def get(self, name: str) -> ModelSpec | None:
        return next((m for m in self.models if m.name == name), None)


def load_registry(path: str | Path) -> Registry:
    data = yaml.safe_load(Path(path).read_text())
    return Registry.model_validate(data)
