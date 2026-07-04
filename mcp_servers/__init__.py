"""mcp_servers — MCP servers exposing internal context to AI assistants.

Named ``mcp_servers`` (not ``mcp``) so it can't shadow the official ``mcp``
Python SDK that the server entrypoints import. The shared tool logic lives in
``context`` (no SDK import, so it's unit-testable); each ``servers/*`` module is
a thin FastMCP wrapper.
"""
