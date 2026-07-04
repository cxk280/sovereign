"""MCP server: operational runbooks."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_servers import context

mcp = FastMCP("sovereign-runbooks")


@mcp.tool()
def search_runbooks(query: str, k: int = 5) -> str:
    """Search on-call and operational runbooks relevant to the query."""
    return context.search_runbooks(query, k)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
