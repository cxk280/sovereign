# adoption

Measure whether the platform is actually helping — the "drive adoption and measure impact" surface.

- [`collector.py`](./collector.py) — parses the gateway's Prometheus `/metrics` (requests by task)
  and combines it with IDE/CI acceptance signals into an **impact report**: total requests,
  acceptance rate, and estimated hours saved. Feeds the dashboard's Adoption view.
- [`grafana-dashboard.json`](./grafana-dashboard.json) — a Grafana dashboard over the gateway metrics
  (requests/sec by task, p95 latency, tokens/sec, error rate).

_Built in build-order Step 6._
