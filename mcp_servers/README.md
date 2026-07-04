# mcp

[Model Context Protocol](https://modelcontextprotocol.io) servers that expose an org's **internal
context** to any MCP-capable AI assistant (Claude Code, Cursor, the gateway) — without that context
ever leaving your infrastructure.

Four servers, each over the synthetic knowledge in [`sample_data/`](../sample_data), backed by the
[`rag`](../rag) retrieval layer:

- **codebase** — `search_code`, `get_file`, `find_symbol`
- **runbooks** — `search_runbooks`, `get_runbook`
- **incidents** — `query_incidents`, `get_incident`, `similar_incidents`
- **architecture** — `search_arch_docs`, `get_adr`

_Built in build-order Step 2._
