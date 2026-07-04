# Architecture Decision Records

Short records of the load-bearing technical decisions in `sovereign` — what was chosen, what was
considered, and why. Each is a snapshot of the reasoning at decision time, not a living spec; when a
decision changes, a new ADR supersedes the old one rather than editing history.

Format: [Michael Nygard's ADR template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html).

| # | Decision | Status |
|---|---|---|
| [0001](./0001-serving-engine.md) | Serving engine — vLLM (GPU) + Ollama/llama.cpp (local); SGLang & TGI as alternatives | Accepted |
| [0002](./0002-custom-gateway-vs-litellm.md) | A custom FastAPI gateway instead of LiteLLM | Accepted |
| [0003](./0003-qdrant-vs-pgvector.md) | Qdrant as the vector store, over pgvector | Accepted |
| [0004](./0004-local-vs-vultr-gpu.md) | Dual deployment — local `docker-compose` and Vultr GPU/VKE | Accepted |

Related: [`../architecture.md`](../architecture.md) (system overview) ·
[`../tradeoffs.md`](../tradeoffs.md) (model/quant/cost).
