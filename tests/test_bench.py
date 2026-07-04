"""Benchmark produces sensible latency/throughput metrics with a stub client."""

from eval.bench import benchmark
from eval.client import StubClient


def test_benchmark_reports_metrics() -> None:
    client = StubClient("stub", lambda p: "one two three four five")
    res = benchmark(client, ["a", "b", "c"])
    assert res.model == "stub"
    assert res.requests == 3
    assert res.avg_latency_s >= 0.0
    assert res.tokens_per_s > 0.0
    assert set(res.as_dict()) == {"model", "requests", "avg_latency_s", "tokens_per_s"}
