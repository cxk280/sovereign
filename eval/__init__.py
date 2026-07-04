"""eval — evaluate and curate open models, and run the model lifecycle.

Benchmarks candidate models on code-gen / code-review / test-gen, produces a
leaderboard + charts, writes the winning model per task back into the gateway
registry (curation), and provides quantization + latency/throughput benchmarking
and registry promotion/rollback (lifecycle).

Everything runs against the gateway's OpenAI-compatible endpoint, so any served
model is evaluable; tests use a deterministic StubClient (no network).
"""
