"""sovereign gateway — OpenAI-compatible model router + registry.

The gateway is the single stable endpoint every client (IDE, CLI, CI) targets.
It resolves each request to a concrete registered model (by explicit name, by
task, or the default), proxies to the appropriate serving backend (local
Ollama/llama.cpp for $0 dev, vLLM on Vultr GPU for prod), and records metrics.
"""

from gateway.app import app_factory, create_app

__all__ = ["app_factory", "create_app"]
