"""MCP server: codebase context."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_servers import context

mcp = FastMCP("sovereign-codebase")


@mcp.tool()
def search_code(query: str, k: int = 5) -> str:
    """Search the internal codebase for snippets relevant to the query."""
    return context.search_code(query, k)


@mcp.tool()
def get_file(path: str) -> str:
    """Return the full contents of a file in the internal codebase."""
    return context.get_file(path)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
