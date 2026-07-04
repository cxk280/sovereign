"""Prometheus metrics — the reliability/observability surface for the gateway.

Scraped at ``/metrics`` and rendered by the adoption dashboard + Grafana (Step 6).
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

REQUESTS = Counter(
    "sovereign_gateway_requests_total",
    "Chat completion requests handled by the gateway.",
    ["model", "task", "status"],
)

LATENCY = Histogram(
    "sovereign_gateway_request_latency_seconds",
    "End-to-end gateway latency per model.",
    ["model"],
)

TOKENS = Counter(
    "sovereign_gateway_tokens_total",
    "Tokens processed, by model and kind (prompt/completion).",
    ["model", "kind"],
)
