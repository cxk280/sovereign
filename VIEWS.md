# VIEWS

Verbal description of every view in `sovereign`. The **only** user-facing UI is the operator
**dashboard** (build-order Step 5). Everything else is CLI, API, MCP, or CI — no graphical views.

> **Design gate:** the dashboard is greenfield UI. Per project rules, the view descriptions below
> are finalized here **first**, then mocked in **Figma** and **approved** before any dashboard code
> is written. This file is a **stub** until Step 5; the sections below name the intended views so the
> scope is visible early. They are placeholders, not yet the approved spec.

## Dashboard views (to be detailed & mocked in Step 5)

1. **Overview** — platform health at a glance: which models are live, request rate, p50/p95 latency,
   tokens/sec, backend (local vs Vultr GPU), error rate.
2. **Model registry** — table of registered models (name, version, quantization, task tags, backend,
   status) and the active routing rules that map tasks → models.
3. **Evaluation leaderboard** — ranked model scores across code-gen / code-review / test-gen, with
   the rendered comparison charts from `eval/`.
4. **Adoption & impact** — usage over time, acceptance signals from IDE/CI, estimated time saved.
5. **Context browser** — read-only explorer of the indexed internal knowledge (codebase, runbooks,
   incidents, architecture) that the MCP/RAG layers serve, with a retrieval-preview search box.

Non-goals for the dashboard: it is an **operator/observability** surface, not a chat UI (chat lives in
the IDE and CLI). No authentication flows are in scope for the portfolio build (single-operator, local).
