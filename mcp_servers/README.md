# mcp_servers

[Model Context Protocol](https://modelcontextprotocol.io) servers that expose an org's **internal
context** to any MCP-capable AI assistant (Claude Code, Cursor, the gateway) — without that context
ever leaving your infrastructure.

> Named `mcp_servers` (not `mcp`) so the package can't shadow the official `mcp` Python SDK that the
> server entrypoints import.

Four servers, each scoped to one context type in [`sample_data/`](../sample_data) and backed by the
[`rag`](../rag) retrieval layer:

| Server | Module | Tools |
|---|---|---|
| **codebase** | `mcp_servers.servers.codebase` | `search_code`, `get_file` |
| **runbooks** | `mcp_servers.servers.runbooks` | `search_runbooks` |
| **incidents** | `mcp_servers.servers.incidents` | `query_incidents` |
| **architecture** | `mcp_servers.servers.architecture` | `search_arch_docs` |

The shared tool logic lives in [`context.py`](./context.py) (no SDK import, so it's unit-tested
directly); each `servers/*` module is a thin FastMCP wrapper.

## Run a server

```bash
uv sync --extra mcp
uv run python -m mcp_servers.servers.incidents      # speaks MCP over stdio
```

Point any MCP client at it, e.g. in Claude Code / Cursor:

```json
{ "mcpServers": { "sovereign-incidents": { "command": "uv",
  "args": ["run", "python", "-m", "mcp_servers.servers.incidents"] } } }
```

## Retrieval backend

By default the servers build a **zero-setup** index (hashed embeddings + in-memory store over
`sample_data/`) so they run offline with no dependencies. Set `SOVEREIGN_RAG_BACKEND=qdrant` (with a
running Qdrant, after `uv run python -m rag.ingest`) to use the production
sentence-transformers + Qdrant path.
