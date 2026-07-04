"""Gateway settings, loaded from the environment (see .env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class BackendConfig:
    ollama_base_url: str = "http://localhost:11434"
    llamacpp_base_url: str = "http://localhost:8081"
    vllm_base_url: str | None = None
    vllm_api_key: str | None = None


@dataclass(frozen=True)
class Settings:
    host: str = "0.0.0.0"
    port: int = 8080
    registry_path: str = "gateway/registry.yaml"
    local_backend: str = "ollama"
    backends: BackendConfig = field(default_factory=BackendConfig)


def load_settings() -> Settings:
    return Settings(
        host=os.getenv("SOVEREIGN_GATEWAY_HOST", "0.0.0.0"),
        port=int(os.getenv("SOVEREIGN_GATEWAY_PORT", "8080")),
        registry_path=os.getenv("SOVEREIGN_REGISTRY_PATH", "gateway/registry.yaml"),
        local_backend=os.getenv("SOVEREIGN_LOCAL_BACKEND", "ollama"),
        backends=BackendConfig(
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            llamacpp_base_url=os.getenv("LLAMACPP_BASE_URL", "http://localhost:8081"),
            vllm_base_url=os.getenv("VLLM_BASE_URL") or None,
            vllm_api_key=os.getenv("VLLM_API_KEY") or None,
        ),
    )
