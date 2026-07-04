# ADR 0003 — Qdrant as the vector store, over pgvector

**Status:** Accepted · **Date:** 2026-07 · **Deciders:** platform

## Context

The [`rag`](../../rag) layer embeds internal knowledge (`sample_data/` → your real code, runbooks,
incidents, architecture docs) with a **local** model and stores the vectors for retrieval by the MCP
servers. The store must:

- Run **entirely inside the sovereignty boundary** — no hosted vector DB.
- Be trivial to stand up locally (Docker) and deployable on **Vultr / VKE**.
- Handle metadata-filtered similarity search (filter by source type, path, service).

The two credible self-hostable options are a **dedicated vector database (Qdrant)** and **pgvector**
(Postgres extension).

## Options considered

| | Qdrant | pgvector |
|---|---|---|
| Purpose-built ANN (HNSW), payload filtering | ✅ first-class | ⚠️ workable, less specialized |
| Local setup | one Docker image | Postgres + extension |
| Scales with corpus growth | designed for it | fine to a point; competes with OLTP load |
| Reuse existing Postgres | — | ✅ if you already run one |
| Ops surface | one more service | none if Postgres already exists |

## Decision

Use **Qdrant** as the default vector store. It is purpose-built for vector search with payload
filtering, ships as a single Docker image (so it fits both `docker-compose` and a VKE Helm chart),
and is a clean, Vultr-friendly dependency.

For **local, offline, zero-setup** runs the MCP servers default to an **in-memory hashed-embedding
index** over `sample_data/` (no Qdrant, no model download); set `SOVEREIGN_RAG_BACKEND=qdrant` to use
the production sentence-transformers + Qdrant path. This keeps the demo runnable anywhere while the
real path is one env var away.

**pgvector is the documented alternative:** a team already running Postgres — and wanting one fewer
service to operate — should prefer pgvector. Because retrieval is behind the `rag` API, swapping the
store is an implementation change, not an interface one.

## Consequences

- **Positive:** strong, filterable similarity search with minimal ops; identical story local and on
  VKE; nothing leaves the boundary.
- **Positive:** the zero-setup in-memory fallback means `mcp_servers` run with no external
  dependencies for demos and unit tests.
- **Negative:** it's a separate service to run in production (vs. reusing an existing Postgres).
  Mitigated by the documented pgvector path for Postgres-centric shops.
