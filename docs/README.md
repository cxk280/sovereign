# docs

Architecture, decision records, and operator/adopter documentation for `sovereign`.

- **[architecture.md](./architecture.md)** — system diagram (Mermaid) and data-flow narrative.
- **[adr/](./adr)** — decision records: serving engine (vLLM vs SGLang vs TGI), gateway vs LiteLLM,
  Qdrant vs pgvector, local vs Vultr GPU.
- **[workshop.md](./workshop.md)** — "adopt private AI in your workflow" hands-on tutorial ($0, ~20 min).
- **[tradeoffs.md](./tradeoffs.md)** — model / quantization / cost tradeoff write-ups feeding the eval report.
- **[traceability.md](./traceability.md)** — role → feature matrix (every JD responsibility → a working deliverable).
- **cost estimate** — the Vultr reference-deployment cost lives with the infra it describes:
  [`infra/cost.md`](../infra/cost.md).

Rendered diagrams (request lifecycle, sovereign-vs-SaaS, architecture, leaderboard) are in
[`assets/`](./assets) and embedded in the root [`README.md`](../README.md).

_Built in build-order Step 8._
