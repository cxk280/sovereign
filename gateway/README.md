# gateway

OpenAI-compatible API gateway: a **model router + registry** in front of every inference backend.

- Speaks `/v1/chat/completions`, `/v1/embeddings`, `/v1/models`.
- **Registry** (`registry.yaml`) tracks each model's version, quantization, task tags, and backend.
- **Router** maps a request's task (code-gen / review / test-gen / chat) to the right model.
- Exposes Prometheus `/metrics` and `/healthz` / `/readyz` for reliability.

Backends: local **Ollama**/**llama.cpp** ($0 dev) or **vLLM** on Vultr Cloud GPU (prod) — swappable
behind the same OpenAI protocol, so IDEs, the CLI, and CI all target one stable endpoint.

_Built in build-order Step 1._
