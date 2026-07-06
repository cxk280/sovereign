# Cost estimate — running sovereign on Vultr

Everyday development is **$0** (local `docker-compose`). Vultr is provisioned only when you want live
GPU serving. Rates are on-demand (confirm current pricing at <https://www.vultr.com/pricing/>).

## Relevant GPU rates

| GPU | VRAM | $/hr | Fit |
|---|---|---|---|
| **NVIDIA A16** | 16 GB | ~$0.47 | 1.5B–7B quantized coder model (the default here) |
| NVIDIA L40S | 48 GB | ~$1.67 | 7B–14B fp16, faster |
| NVIDIA A100 (PCIe) | 80 GB | ~$2.40 | overkill for this workload |

Fixed extras: **VKE control plane is free** (pay only worker nodes); Object Storage ≈ $5/mo; a load
balancer ≈ $10/mo (optional).

## What this project actually costs

| Scenario | GPU | Cost |
|---|---|---|
| **One CPU benchmark run** (`make bench-vultr-cpu`: apply → benchmark → destroy) | none (`vc2-4c-8gb`) | **~$0.05** |
| **One benchmark run** (`make bench-vultr`: apply → benchmark → destroy, ~4h) | A16 | **~$2** |
| Live demo (~8h serving) | A16 | ~$4 |
| Left up a week (24×7) | A16 | ~$79 |
| Always-on for a month (upper bound, not recommended) | A16 / L40S | ~$344 / ~$1,220 |

**Target: under ~$10** to turn "architected" into "measured" — a single `make bench-vultr` produces
real latency/throughput/tokens-per-sec numbers into the eval leaderboard, then tears everything down.

**No GPU credit? `make bench-vultr-cpu`.** The same harness runs against a regular Vultr cloud-compute
instance serving the quantized model with Ollama (OpenAI-compatible, no CUDA). It produces genuinely
measured numbers **on Vultr** for cents — slower than the A16, and the dashboard labels them honestly
as *Vultr CPU compute*, never as GPU. The A16 path is one command away when GPU credit is available.

The larger multi-GPU VKE topology (Helm `values.yaml`, `vllm.gpus > 1` for tensor-parallel) is
architected and costed here but **not stood up** in the $0 build.
