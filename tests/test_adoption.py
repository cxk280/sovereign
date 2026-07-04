"""Adoption collector: parse gateway metrics, compute impact."""

from adoption.collector import build_impact, parse_prometheus, requests_by_task

_METRICS = """
# HELP sovereign_gateway_requests_total Chat completion requests
# TYPE sovereign_gateway_requests_total counter
sovereign_gateway_requests_total{model="qwen",task="code-gen",status="ok"} 10.0
sovereign_gateway_requests_total{model="qwen",task="code-review",status="ok"} 4.0
sovereign_gateway_requests_total{model="qwen",task="code-gen",status="error"} 1.0
"""


def test_parse_prometheus_reads_samples() -> None:
    samples = parse_prometheus(_METRICS)
    assert (
        "sovereign_gateway_requests_total",
        {"model": "qwen", "task": "code-gen", "status": "ok"},
        10.0,
    ) in samples


def test_requests_by_task_sums_ok_only() -> None:
    assert requests_by_task(_METRICS) == {"code-gen": 10.0, "code-review": 4.0}


def test_build_impact_computes_rate_and_hours() -> None:
    report = build_impact({"code-gen": 10.0}, accepted=8, rejected=2, minutes_saved_per_accept=6.0)
    assert report.total_requests == 10.0
    assert abs(report.acceptance_rate - 0.8) < 1e-9
    assert abs(report.est_hours_saved - 0.8) < 1e-9  # 8 * 6 / 60
    assert set(report.as_dict()) == {
        "total_requests",
        "by_task",
        "acceptance_rate",
        "est_hours_saved",
    }
