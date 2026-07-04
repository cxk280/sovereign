"""MCP server: incident history."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_servers import context

mcp = FastMCP("sovereign-incidents")


@mcp.tool()
def query_incidents(query: str, k: int = 5) -> str:
    """Search past incident reports — 'has this failed before, and why?'"""
    return context.query_incidents(query, k)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
