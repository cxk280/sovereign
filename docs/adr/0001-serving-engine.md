# ADR 0001 — Serving engine

**Status:** Accepted · **Date:** 2026-07 · **Deciders:** platform

## Context

The platform serves open models (Qwen2.5-Coder, Llama, Mistral, DeepSeek) for interactive coding,
review, and CI. Two very different environments have to be served from the *same* client interface:

- **Local, $0, no GPU** — everyday development on a laptop (an 8 GB Intel Mac here).
- **Production, Vultr Cloud GPU** — real throughput, CUDA, room to scale to multi-GPU.

The leading options are **vLLM, SGLang, and TGI**, so the choice has to be reasoned,
not defaulted. The non-negotiable constraint is that whatever we pick must speak the **OpenAI
protocol**, so the gateway, IDEs, and CI never learn which engine is underneath.

## Options considered

| Engine | Strengths | Why not (as the primary) |
|---|---|---|
| **vLLM** | PagedAttention → high throughput; continuous batching; mature OpenAI-compatible server; tensor-parallel multi-GPU; AWQ/GPTQ quant | Needs a CUDA GPU — not runnable on the local $0 laptop path |
| **SGLang** | RadixAttention prefix caching, excellent for structured/agentic multi-turn; fast | Younger ecosystem; overlaps vLLM for our workload; still GPU-only |
| **TGI** | Production-hardened (HF), good ops story | Heavier to run; licensing history; no clear win over vLLM here |
| **Ollama / llama.cpp** | Runs a Q4 model on CPU with zero GPU; trivial local setup; GGUF | Not a high-throughput production server |

## Decision

Use **two backends behind one gateway**, chosen per environment:

- **vLLM** is the **production Vultr-GPU target** — OpenAI-compatible, CUDA, multi-GPU
  (tensor-parallel expressed in the Helm chart). It serves an AWQ-quantized coder model on the A16
  benchmark and on VKE.
- **Ollama / llama.cpp** is the **local $0 backend**, serving a Q4 Qwen2.5-Coder on CPU — the
  runnable demo path with no GPU.

**SGLang and TGI are documented alternatives, not dead ends.** Because everything sits behind the
gateway's OpenAI protocol, swapping vLLM for SGLang or TGI is a backend config change, not a client
change — see [`inference/`](../../inference).

## Consequences

- **Positive:** the same `/v1/chat/completions` interface works from laptop to GPU; clients never
  change; the engine is a swappable implementation detail.
- **Positive:** we can demonstrate the full lifecycle (quantize → serve → benchmark) on a real A16
  with vLLM while keeping day-to-day dev free.
- **Negative:** two serving code paths to keep working (mitigated: the gateway and tests target the
  protocol, not the engine).
- **Negative:** vLLM's throughput advantages only appear on GPU; local numbers are CPU-bound and not
  representative of production (called out explicitly wherever numbers are shown).
