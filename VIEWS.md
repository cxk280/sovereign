# VIEWS

Verbal description of every view in `sovereign`. The **only** graphical UI is the operator
**dashboard** (build-order Step 5). Everything else is CLI, API, MCP, or CI — no other views.

> **Design gate:** the dashboard is greenfield UI. These descriptions are finalized here, then mocked
> in **Figma** and **approved** before any dashboard code is written.
>
> **Mocks (v1):** all 5 views — [Figma file](https://www.figma.com/design/W4yVBCLXcDUAXrmU3Uhn91).
> Status: **awaiting user approval** before any `dashboard/` code is written (built via `/factory`).

## Design language

- **Shell:** left **sidebar** (the `sovereign` wordmark + shield mark; nav items: Overview, Registry,
  Leaderboard, Adoption, Context) and a **top bar** (current view title, a backend pill showing
  `local` vs `Vultr GPU`, and a health dot). Content area to the right.
- **Palette:** indigo `#4F46E5` primary, emerald `#10B981` accent (healthy / sovereign), amber/red for
  warn/error, slate neutrals on a near-white `#F8FAFC` canvas. Cards are white, rounded (12–16px),
  1.5px slate border. Font: Inter. Theme: light (single theme for the portfolio build).
- **Primitives:** stat tile (label + big value + delta), data table, the eval bar chart, a small
  time-series sparkline, status pills.

## Views

### 1. Overview (default)
Platform health at a glance:
- A row of **stat tiles**: Models live, Requests/min, p50 latency, p95 latency, Tokens/sec, Error rate
  — each with a small trend delta.
- A **requests-over-time** area/sparkline for the last hour.
- A compact **backend panel**: which backend is serving (`Ollama local` / `vLLM · Vultr A16`), model
  loaded, and a health/readiness indicator.

### 2. Model registry
- A **table** of registered models: name, version, quantization, task tags, backend, status
  (active/candidate).
- A **routing panel**: task → model mappings (code-gen, code-review, test-gen, chat) with the default
  route highlighted. Read-only in the portfolio build.

### 3. Evaluation leaderboard
- The **grouped bar chart** from `eval/` (pass rate per model per task).
- A **ranked table** (model, code-gen, code-review, test-gen, overall) sorted by overall, winner
  highlighted, with a note when a model is the curated route for a task.

### 4. Adoption & impact
- **Stat tiles**: total requests, acceptance rate (IDE/CI), estimated hours saved.
- A **usage-over-time** chart (requests by day) and a small **by-surface** breakdown (IDE / CLI / CI).

### 5. Context browser
- A **source inventory** grouped by type (codebase, runbooks, incidents, architecture) with document
  counts and chunk counts.
- A **retrieval-preview** search box: type a query, see the top grounded chunks (title · path ·
  snippet · score) the MCP layer would return. Read-only.

Non-goals: no chat UI (chat lives in the IDE/CLI), no authentication flows (single-operator, local).
