# Tradeoffs — model, quantization, and cost

The reasoning behind the model choices, quantization levels, and hardware sizing. These are the
tradeoffs the [`eval`](../eval) harness turns into evidence, and the [`gateway`](../gateway) registry
turns into behavior. Defaults here are recommendations, not lock-in — every one is swappable behind
the gateway.

## Model families

The platform features the open families named in the target role, matched to the tasks they're best
at. The eval harness scores them on **code-gen** (generated code executed against hidden tests),
**test-gen** (generated tests run against a reference), and **code-review** (planted-bug detection).

| Family | Where it fits | Tradeoff |
|---|---|---|
| **Qwen2.5-Coder** | Default coder — code-gen, review, test-gen | Strongest code performance per parameter in this class; small variants run on CPU. The local default. |
| **DeepSeek-Coder** | Code-gen alternative | Competitive on code; another data point for curation rather than a single-vendor bet. |
| **Llama-3.x** | General chat / reasoning | Broad, well-supported generalist; less code-specialized than Qwen-Coder. |
| **Mistral** | General / lightweight | Efficient generalist; good fallback where a coder model is overkill. |

**Why not one big model for everything?** Routing per task (see
[registry.yaml](../gateway/registry.yaml)) lets a small, fast coder model handle the high-volume
code paths while a generalist takes open-ended chat — better latency and cost than forcing one large
model to do all of it. Curation (`eval --curate`) writes the measured winner per task back into
routing, so the choice is evidence-driven, not a hunch.

## Quantization

Quantization shrinks a model so it fits cheaper hardware and runs faster, trading a little accuracy.
The lifecycle scripts ([`eval/quantize.py`](../eval)) produce GGUF (llama.cpp) and AWQ (vLLM)
variants; [`eval/bench.py`](../eval) measures the cost of each.

| Level | Size vs fp16 | Quality | Use |
|---|---|---|---|
| **fp16** | 100% | reference | GPU with VRAM to spare; the accuracy baseline |
| **Q8** | ~50% | near-lossless | when you can afford it and want max quality below fp16 |
| **Q5_K_M** | ~35% | very good | balanced GPU/CPU serving |
| **Q4_K_M** | ~30% | good; slight degradation | **local $0 default** — a 1.5B coder runs on an 8 GB CPU laptop |
| **AWQ (4-bit)** | ~30% | good; GPU-optimized | the **vLLM production path** on Vultr GPU |

**Rule of thumb:** start at Q4_K_M locally, move to AWQ on GPU for production throughput, and only
climb to Q5/Q8/fp16 if the eval scores for your task justify the extra VRAM and latency. Don't guess
which — `bench.py` gives you latency / throughput / tokens-per-sec per model×quant to decide on
evidence.

## Hardware / cost

Full detail lives in [`infra/cost.md`](../infra/cost.md); the shape of the tradeoff:

| Path | Hardware | Cost | When |
|---|---|---|---|
| **Local** | CPU laptop (8 GB), Q4 model | **$0** | everyday dev; the default |
| **A16** (16 GB) | 1.5B–7B quantized coder | ~$0.47/hr | the measured benchmark; small prod |
| **L40S** (48 GB) | 7B–14B fp16, faster | ~$1.67/hr | when quality/throughput needs the headroom |
| **A100** (80 GB) | — | ~$2.40/hr | overkill for this workload |

The discipline that makes the Vultr numbers **real and cheap**: `make bench-vultr` applies an A16,
serves vLLM, runs the eval/benchmark harness, pushes results to Object Storage, and **destroys** the
instance — a single run lands under ~$10 and produces measured leaderboard numbers instead of
projections. See [ADR 0004](./adr/0004-local-vs-vultr-gpu.md).

## The three-way tension

Every real decision here is a triangle of **quality ↔ cost ↔ latency**:

- Bigger model or higher precision → better quality, more VRAM/$, slower.
- Heavier quantization or smaller model → cheaper and faster, some quality lost.
- Task routing is the lever that lets you pick a different point on the triangle **per task** instead
  of once for the whole platform.

The point of the eval + benchmark harness is to make that triangle **measured** for your models on
your hardware, so the registry routes on numbers rather than reputation.
