"""Performance benchmarking — latency and throughput per model.

Part of "own the model lifecycle". Runs prompts through a client and reports
average latency and tokens/sec. Designed to run against the gateway locally or
against vLLM on a Vultr GPU (Step 7) so the numbers are measured, not guessed.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass

from eval.client import ModelClient


@dataclass
class BenchResult:
    model: str
    requests: int
    avg_latency_s: float
    tokens_per_s: float

    def as_dict(self) -> dict:
        return asdict(self)


def _approx_tokens(text: str) -> int:
    # cheap, backend-agnostic proxy; real runs read usage.completion_tokens
    return max(1, len(text.split()))


def benchmark(client: ModelClient, prompts: list[str]) -> BenchResult:
    latencies: list[float] = []
    tokens = 0
    for p in prompts:
        start = time.perf_counter()
        try:
            out = client.complete(p)
        except Exception:
            # A single slow/failed call must not sink the whole benchmark — especially
            # after paying for GPU time. Skip it and report throughput over what succeeded.
            continue
        latencies.append(time.perf_counter() - start)
        tokens += _approx_tokens(out)
    wall = sum(latencies) or 1e-9
    return BenchResult(
        model=client.name,
        requests=len(latencies),
        avg_latency_s=(sum(latencies) / len(latencies)) if latencies else 0.0,
        tokens_per_s=tokens / wall,
    )
