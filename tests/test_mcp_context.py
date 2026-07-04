"""MCP context tools return grounded results and sandbox file access."""

from mcp_servers import context


def test_query_incidents_returns_grounded_text() -> None:
    out = context.query_incidents("connection exhaustion")
    assert "INC-2025-002" in out or "exhaustion" in out.lower()


def test_search_runbooks_finds_the_failover_runbook() -> None:
    out = context.search_runbooks("postgres failover connection budget")
    assert "failover" in out.lower() or "connection" in out.lower()


def test_get_file_reads_inside_the_root() -> None:
    out = context.get_file("architecture/system-overview.md")
    assert "Meridian" in out


def test_get_file_blocks_path_traversal() -> None:
    assert "denied" in context.get_file("../../../../etc/passwd").lower()
