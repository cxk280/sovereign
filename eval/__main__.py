"""CLI: benchmark models through the gateway, emit a leaderboard + chart, curate.

uv run python -m eval --models qwen2.5-coder:1.5b --gateway http://localhost:8080
uv run python -m eval --models a,b --curate        # write winners into the registry
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from eval.charts import render_leaderboard_chart
from eval.client import GatewayClient, ModelClient
from eval.leaderboard import build_leaderboard, to_markdown
from eval.registry_ops import curate_registry
from eval.runner import run_suite


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="eval")
    ap.add_argument("--models", required=True, help="comma-separated model names to evaluate")
    ap.add_argument(
        "--gateway", default=os.getenv("SOVEREIGN_GATEWAY_URL", "http://localhost:8080")
    )
    ap.add_argument("--out", default="eval/results")
    ap.add_argument("--registry", default="gateway/registry.yaml")
    ap.add_argument(
        "--curate", action="store_true", help="write winning model per task to registry"
    )
    args = ap.parse_args(argv)

    clients: list[ModelClient] = [
        GatewayClient(args.gateway, m.strip()) for m in args.models.split(",") if m.strip()
    ]
    lb = build_leaderboard(run_suite(clients))

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "leaderboard.json").write_text(json.dumps(lb, indent=2))
    (out / "leaderboard.md").write_text(to_markdown(lb))
    render_leaderboard_chart(lb, out / "leaderboard.png")
    print(to_markdown(lb))

    if args.curate:
        applied = curate_registry(args.registry, lb)
        print(f"\nCurated routes: {applied}")


if __name__ == "__main__":
    main()
