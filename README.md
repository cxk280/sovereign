# sovereign

**A self-hosted, data-sovereign AI platform for engineering teams.**

Self-host open models on your own GPUs so proprietary code, incident history, and runbooks
**never leave your infrastructure** for a third-party AI SaaS. `sovereign` gives an engineering
org a private code assistant, context-aware [MCP](https://modelcontextprotocol.io) servers over its
own internal knowledge, AI-assisted CI/CD, a model registry with routing and evaluation, and
one-command deployment to [Vultr](https://www.vultr.com) Cloud GPU.

> **Status:** early build, in progress. See the build-order checklist below.
>
> **Independent portfolio project — not affiliated with or endorsed by Vultr.** All data under
> [`sample_data/`](./sample_data) is fictitious and synthetic. See [`NOTICE`](./NOTICE).

## Why "sovereign"

The moment your code assistant is a hosted SaaS, your source, your incident post-mortems, and your
architecture docs become someone else's training data and someone else's breach surface. `sovereign`
keeps **both the model and the data in-house**: open-weights models served on hardware you control,
context injected from your own systems, zero required egress. Data sovereignty and AI capability at
the same time.

## What it does — mapped to the work

Every capability maps to a concrete piece of the platform:

| Capability | Where it lives |
|---|---|
| Evaluate & curate open models (Qwen, Llama, Mistral, DeepSeek) for code-gen / review / test-gen | [`eval/`](./eval) |
| MCP servers exposing internal context — codebase, runbooks, incidents, architecture docs | [`mcp/`](./mcp) |
| AI in CI/CD — automated code review, test generation, MR summarization (GitLab) | [`.gitlab-ci.yml`](./.gitlab-ci.yml) · [`ci/`](./ci) |
| Model lifecycle — versioning, routing, quantization, benchmarking | [`gateway/`](./gateway) |
| LLM inference — vLLM on GPU (prod) / llama.cpp · Ollama (local) | [`inference/`](./inference) |
| RAG over internal knowledge with a local embedding model + vector DB | [`rag/`](./rag) |
| IDE tooling backed by an internal, OpenAI-compatible endpoint | [`ide/`](./ide) |
| Adoption & impact measurement | [`adoption/`](./adoption) |
| Reliability — health checks, Prometheus/Grafana observability | across services |
| Infrastructure as code — Vultr Cloud GPU, VKE, Object Storage | [`infra/`](./infra) |

## Architecture (at a glance)

```
 IDE / CLI / GitLab CI ──▶ gateway (OpenAI-compatible router + registry)
                                │            │
                                ▼            ▼
                      local: Ollama /   prod: vLLM on
                      llama.cpp (CPU)   Vultr Cloud GPU
                                │
        MCP servers ◀───────────┴───────────▶ RAG (embeddings → Qdrant)
     (codebase · runbooks ·                     over sample_data/
      incidents · architecture)
```

Two run profiles, one codebase:
- **Local ($0):** `docker-compose up` runs the gateway, a small quantized model via Ollama/llama.cpp,
  and Qdrant on a laptop. This is the runnable demo path.
- **Vultr (production target):** Terraform + Helm provision Cloud GPU + VKE + Object Storage and serve
  the same models with vLLM. Shipped as reviewable IaC and cost estimates (`terraform plan`), not spend.

## Quick start (local)

```bash
cp .env.example .env          # adjust if needed; defaults target local services
uv sync --extra gateway --extra dev
docker compose up -d          # gateway + Ollama/llama.cpp + Qdrant   (added in Step 1–2)
curl localhost:8080/v1/models
```

## Build order

- [x] **0 — Scaffold + governance**
- [x] **1 — Inference + gateway (local $0)**
- [ ] 2 — RAG + MCP servers
- [ ] 3 — Eval + leaderboard
- [ ] 4 — GitLab CI/CD (live)
- [ ] 5 — Dashboard (design-gated UI)
- [ ] 6 — IDE tooling + adoption metrics
- [ ] 7 — Infra-as-code (Vultr)
- [ ] 8 — Docs & polish

## Repository layout

See the capability table above; each directory has its own `README.md`. Synthetic internal knowledge
that the MCP/RAG layers index lives in [`sample_data/`](./sample_data). Design docs and ADRs live in
[`docs/`](./docs).

## License

[MIT](./LICENSE). Third-party model names are trademarks of their respective owners.
