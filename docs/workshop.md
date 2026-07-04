# Workshop — adopt private AI in your workflow

A hands-on tutorial: stand up `sovereign` locally for **$0**, then use it three ways an engineer
actually would — from the terminal, grounded in your own knowledge, and in your editor. Everything
here runs on a laptop with no GPU. No code or prompt leaves your machine.

**Time:** ~20 minutes · **Cost:** $0 · **Prereqs:** Docker, [`uv`](https://docs.astral.sh/uv/), and
~4 GB free for a small model.

---

## 0. Get the platform running

```bash
git clone https://github.com/cxk280/sovereign
cd sovereign
cp .env.example .env

uv sync --extra gateway --extra dev
docker compose up -d ollama gateway
docker compose exec ollama ollama pull qwen2.5-coder:1.5b
```

Confirm it's alive and the registry is wired:

```bash
curl -s localhost:8080/healthz
curl -s localhost:8080/v1/models      # should list the task routes from registry.yaml
```

You now have one OpenAI-compatible endpoint at `localhost:8080`, routing tasks to a small quantized
coder model on your CPU.

---

## 1. Talk to it — the terminal

The lowest-friction surface is the `sov` CLI ([`ide/`](../ide)):

```bash
uv run sov chat "Explain what a circuit breaker is in one paragraph."
uv run sov review path/to/some_file.py     # AI code review of a file
uv run sov test  path/to/some_file.py       # suggested pytest tests
```

Or hit the raw endpoint with any OpenAI client — note the `model` is a **task name**, not a model:

```bash
curl -s localhost:8080/v1/chat/completions \
  -d '{"model":"code-review","messages":[{"role":"user","content":"Review this diff for bugs."}]}'
```

The gateway's router resolved `code-review` → the model tagged for that task in
[`registry.yaml`](../gateway/registry.yaml). **Checkpoint:** you got a completion back, and nothing
left your laptop.

---

## 2. Ground it in your own knowledge — RAG + MCP

A generic assistant guesses about your systems. Point it at *your* runbooks, incidents, and
architecture and it answers from them instead. The repo ships **synthetic** knowledge for a made-up
company ("Meridian Logistics") under [`sample_data/`](../sample_data) so this works in public.

Run an MCP server — it needs no setup (it builds a zero-dependency in-memory index by default):

```bash
uv sync --extra mcp
uv run python -m mcp_servers.servers.incidents      # speaks MCP over stdio
```

Point an MCP client at it. In Claude Code or Cursor:

```json
{ "mcpServers": { "sovereign-incidents": { "command": "uv",
  "args": ["run", "python", "-m", "mcp_servers.servers.incidents"] } } }
```

Now ask your assistant something only your history knows — *"Has the checkout service failed on a
Redis timeout before? What did we do?"* — and it will call `query_incidents`, retrieve the matching
post-mortem, and answer from it. Swap in the other servers (`codebase`, `runbooks`, `architecture`)
the same way.

**Make it yours:** point [`rag/ingest`](../rag) at your real repo, runbooks, and incidents (set
`SOVEREIGN_RAG_BACKEND=qdrant` with a running Qdrant for the production path). Everything is embedded
and searched locally — see [ADR 0003](./adr/0003-qdrant-vs-pgvector.md).

---

## 3. Put it in your editor — IDE tooling

Three editor surfaces, all pointed at the same internal endpoint ([`ide/`](../ide)):

- **Continue** — copy [`ide/continue/config.json`](../ide/continue/config.json) into your Continue
  config for chat **and** tab-autocomplete against the gateway (telemetry off).
- **Cursor** — override Cursor's OpenAI base URL to `http://localhost:8080` (see
  [`ide/cursor/`](../ide/cursor)).
- **VS Code extension** — [`ide/vscode/`](../ide/vscode): a Copilot alternative — inline
  fill-in-the-middle completions via `/v1/completions`, plus a "Review Selection" command.

Autocomplete rides the gateway's `/v1/completions` (FIM) endpoint. **Checkpoint:** you're getting
inline completions from a model on your own machine, not a cloud assistant.

---

## 4. Wire it into CI (optional, GitLab)

The same gateway backs AI in your pipeline ([`ci/`](../ci)): automated code review, test generation,
and MR summaries, each calling the internal endpoint so **no diff leaves for a third party**. Mirror
the repo to GitLab, set `SOVEREIGN_GATEWAY_URL` and a `GITLAB_TOKEN`, use a runner that can reach the
gateway, and open an MR — three notes appear. Details in [`ci/README.md`](../ci/README.md).

---

## 5. Measure whether it's helping

Adoption isn't a vibe. The [`adoption`](../adoption) collector reads the gateway's Prometheus
`/metrics` and combines request volume with IDE/CI acceptance signals into an impact report (requests
by task, acceptance rate, estimated hours saved), and ships a
[Grafana dashboard](../adoption/grafana-dashboard.json) over the same metrics.

---

## Where to go next

- **Understand the shape:** [`architecture.md`](./architecture.md).
- **Why each choice:** the [ADRs](./adr).
- **Which model / quant / GPU:** [`tradeoffs.md`](./tradeoffs.md).
- **Go to production on Vultr:** [`infra/README.md`](../infra/README.md) and
  [`infra/cost.md`](../infra/cost.md).
- **See the evidence:** run the eval harness (`uv run python -m eval …`) for a leaderboard
  ([`eval/README.md`](../eval/README.md)).
