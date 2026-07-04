"""Parse gateway Prometheus metrics + acceptance signals → an impact report."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

_SAMPLE = re.compile(r"^(?P<name>\w+)\{(?P<labels>[^}]*)\}\s+(?P<value>[0-9.eE+-]+)\s*$")


def parse_prometheus(text: str) -> list[tuple[str, dict[str, str], float]]:
    """Return (metric_name, labels, value) for each non-comment sample line."""
    out: list[tuple[str, dict[str, str], float]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _SAMPLE.match(line)
        if not m:
            continue
        labels = dict(re.findall(r'(\w+)="([^"]*)"', m.group("labels")))
        out.append((m.group("name"), labels, float(m.group("value"))))
    return out


def requests_by_task(text: str) -> dict[str, float]:
    """Successful gateway requests grouped by task."""
    totals: dict[str, float] = {}
    for name, labels, value in parse_prometheus(text):
        if name == "sovereign_gateway_requests_total" and labels.get("status") == "ok":
            task = labels.get("task", "unknown")
            totals[task] = totals.get(task, 0.0) + value
    return totals


@dataclass
class ImpactReport:
    total_requests: float
    by_task: dict[str, float]
    acceptance_rate: float
    est_hours_saved: float

    def as_dict(self) -> dict:
        return asdict(self)


def build_impact(
    by_task: dict[str, float],
    accepted: int,
    rejected: int,
    minutes_saved_per_accept: float = 8.0,
) -> ImpactReport:
    handled = accepted + rejected
    return ImpactReport(
        total_requests=sum(by_task.values()),
        by_task=by_task,
        acceptance_rate=(accepted / handled) if handled else 0.0,
        est_hours_saved=accepted * minutes_saved_per_accept / 60.0,
    )
