"""MCP server: architecture docs and decision records."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_servers import context

mcp = FastMCP("sovereign-architecture")


@mcp.tool()
def search_arch_docs(query: str, k: int = 5) -> str:
    """Search architecture overviews and ADRs (decision records) for the query."""
    return context.search_arch_docs(query, k)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
