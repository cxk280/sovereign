"""`sov` — chat, review a file, or generate tests from the terminal.

sov chat "how do I paginate this endpoint?"
sov review path/to/file.py
sov test path/to/file.py
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

_TASK = {"chat": "chat", "review": "code-review", "test": "test-gen"}


def build_prompt(command: str, text: str) -> str:
    if command == "review":
        return f"Review this code for correctness, security, and style issues:\n\n{text}"
    if command == "test":
        return f"Write focused pytest tests for this code:\n\n{text}"
    return text


def dispatch(command: str, text: str, client: Any) -> str:
    return client.complete(build_prompt(command, text), task=_TASK[command])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="sov")
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("chat").add_argument("message", nargs="+")
    sub.add_parser("review").add_argument("file")
    sub.add_parser("test").add_argument("file")
    args = ap.parse_args(argv)

    text = " ".join(args.message) if args.command == "chat" else Path(args.file).read_text()

    from ide.client import GatewayClient

    client = GatewayClient(os.getenv("SOVEREIGN_GATEWAY_URL", "http://localhost:8080"))
    print(dispatch(args.command, text, client))
    return 0


if __name__ == "__main__":
    sys.exit(main())
