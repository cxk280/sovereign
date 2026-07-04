# Role → feature traceability

`sovereign` was built so that every responsibility of the target role — **Senior AI Platform
Engineer, Core Cloud Engineering** — maps onto a working, linkable deliverable in this repo. This
matrix is the map. Each row is a JD responsibility; the right column is where you can go run it.

| # | Role responsibility | Where it's demonstrated | Status |
|---|---|---|---|
| 1 | **Evaluate & curate open models** (Llama, Mistral, Qwen, DeepSeek) | [`eval/`](../eval) — harness scores code-gen / review / test-gen; `--curate` writes the winner per task back into registry routing | ✅ working |
| 2 | **Build MCP servers** over internal context (code, runbooks, incidents, arch) | [`mcp_servers/`](../mcp_servers) — 4 servers over synthetic internal data, backed by RAG | ✅ working |
| 3 | **Integrate AI into GitLab CI/CD** (auto review, test-gen, MR summaries) | [`.gitlab-ci.yml`](../.gitlab-ci.yml) + [`ci/`](../ci) — three AI jobs calling the internal gateway | ✅ working; runs live on the GitLab mirror |
| 4 | **Own the model lifecycle** — versioning, routing, quantization, benchmarking | [`gateway/`](../gateway) registry+router; [`eval/`](../eval) `quantize.py` / `bench.py` / `registry_ops.py` (promote/rollback) | ✅ working |
| 5 | **LLM inference** (vLLM / SGLang / TGI), GPU (CUDA, multi-GPU) | [`inference/`](../inference) — vLLM on Vultr GPU, llama.cpp/Ollama local; SGLang/TGI in [ADR 0001](./adr/0001-serving-engine.md) | ✅ working (vLLM measured on A16) |
| 6 | **RAG + vector DB** | [`rag/`](../rag) — local embeddings → Qdrant; pgvector in [ADR 0003](./adr/0003-qdrant-vs-pgvector.md) | ✅ working |
| 7 | **IDE tooling** backed by internal endpoints | [`ide/`](../ide) — `sov` CLI + Continue + Cursor + VS Code FIM extension (Copilot alternative) | ✅ working |
| 8 | **Drive adoption; measure impact** | [`adoption/`](../adoption) — impact report from gateway metrics + acceptance signals; Grafana dashboard | ✅ working |
| 9 | **Docs & workshops; communicate tradeoffs** | [`docs/`](.) — [architecture](./architecture.md), [ADRs](./adr), [workshop](./workshop.md), [tradeoffs](./tradeoffs.md), this matrix | ✅ working |
| 10 | **Platform reliability** | Gateway `/healthz` · `/readyz` · Prometheus `/metrics`; [`adoption/grafana-dashboard.json`](../adoption/grafana-dashboard.json) | ✅ working |
| 11 | **Infrastructure as code** (Vultr GPU / VKE / Object Storage) | [`infra/`](../infra) — Terraform + Helm; `make tf-plan` / `helm-lint` (plan-only, $0) | ✅ working (plan) |

## The sovereignty thesis, in one line

Each row above stays **inside your infrastructure** — the model and the data never leave. That is
the platform's reason to exist: you can't ship proprietary code, incident history, or runbooks to a
third-party AI SaaS, so you self-host open models on your own (Vultr) GPUs and keep both the AI and
the data sovereign.

## What's measured vs. architected — the honest boundary

Two lines are drawn deliberately, and the docs never blur them:

- **Measured:** single-**A16** latency / throughput / tokens-per-sec in the leaderboard come from a
  real `make bench-vultr` run on Vultr hardware — apply → serve vLLM → benchmark → destroy
  ([ADR 0004](./adr/0004-local-vs-vultr-gpu.md)).
- **Architected & costed, not stood up:** the larger multi-GPU, tensor-parallel VKE topology is
  shipped as Helm + Terraform (`vllm.gpus > 1`) and costed in [`infra/cost.md`](../infra/cost.md),
  but not run in the $0 build.
- **Mock-gated:** the operator **dashboard** (eval leaderboard, registry/routing, live metrics,
  adoption) is specified in [`VIEWS.md`](../VIEWS.md) and goes through Figma-mock approval before UI
  code — greenfield UI held behind its design gate by project rule.

## Data hygiene (public repo)

Everything under [`sample_data/`](../sample_data) is **synthetic** — a fictitious company ("Meridian
Logistics") standing in for real internal knowledge so the retrieval and MCP layers have something to
index in public. Point the ingestion at your own sources to make it yours. Licensed [MIT](../LICENSE);
this is an independent project, **not affiliated with or endorsed by Vultr** (see [`NOTICE`](../NOTICE)).
