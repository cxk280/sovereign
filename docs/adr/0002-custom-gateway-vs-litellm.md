# ADR 0002 — A custom FastAPI gateway instead of LiteLLM

**Status:** Accepted · **Date:** 2026-07 · **Deciders:** platform

## Context

Every client — IDEs, the `sov` CLI, CI jobs, the eval harness — needs to reach models through **one
stable, OpenAI-compatible endpoint**, with a **registry** (model versions, quantization, task tags,
backend) and a **router** that maps a request's task to the right model. Off-the-shelf proxies exist;
[LiteLLM](https://github.com/BerriAI/litellm) is the obvious one and covers most of this.

The platform's whole point, though, is to **demonstrate ownership of the model lifecycle** — routing,
quantization, benchmarking, promotion/rollback — for a role that is exactly that work. A black-box
proxy would hide the thing we most need to show.

## Options considered

- **LiteLLM proxy** — mature, many providers, OpenAI-compatible, built-in routing/fallbacks. But the
  registry/routing/lifecycle logic lives inside someone else's abstraction; extending it to write
  eval results back into routing, or to expose our own registry shape, means fighting the framework.
- **A managed gateway (cloud AI gateway)** — off the table: it breaks the sovereignty guarantee by
  putting a third party in the request path.
- **Custom FastAPI gateway** — a few hundred lines: OpenAI-compatible routes, a YAML registry, a task
  router, Prometheus metrics, health/readiness. Full control over the lifecycle surface.

## Decision

Build a **custom FastAPI gateway**. It owns:

- `/v1/chat/completions`, `/v1/completions` (FIM), `/v1/embeddings`, `/v1/models`, streaming.
- A **registry** ([`registry.yaml`](../../gateway/registry.yaml)) of versions, quant level, task
  tags, and backend per model.
- A **router** mapping task → model, which the [`eval`](../../eval) harness writes back into via
  `--curate` (evidence → behavior) and `registry_ops.py` (`promote` / `rollback`).
- Prometheus `/metrics` + `/healthz` / `/readyz` for the reliability and adoption surfaces.

LiteLLM is recorded here as the **off-the-shelf alternative**: for a team that only needs a proxy and
not a lifecycle demonstration, LiteLLM is the pragmatic choice and this gateway's OpenAI surface
means it could be dropped in later with no client changes.

## Consequences

- **Positive:** the model lifecycle is visible and testable — routing, curation, promotion/rollback
  are our code, unit-tested with fakes.
- **Positive:** no third party in the request path; nothing to trust but our own process.
- **Positive:** the registry shape is exactly what the dashboard and eval need, with no adapter.
- **Negative:** we maintain provider adapters and edge cases LiteLLM would have handled. Acceptable:
  the backend surface is small (Ollama/llama.cpp, vLLM) and speaks one protocol.
