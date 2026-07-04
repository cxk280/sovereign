# ADR 0004 — Dual deployment: local `docker-compose` and Vultr GPU/VKE

**Status:** Accepted · **Date:** 2026-07 · **Deciders:** platform, user

## Context

This is a public portfolio project with two competing requirements:

- **Near-$0.** Everyday development must cost nothing and run on a laptop with no GPU.
- **Real Vultr proof.** The platform must genuinely run on Vultr Cloud GPU / VKE / Object Storage —
  and the leaderboard should carry **measured** numbers, not projections — because that is the
  target environment for the role.

Spending money is outward-facing and must be **user-authorized**, never automatic. So the deployment
model has to make free the default and paid an explicit, bounded, teardown-disciplined action.

## Options considered

- **Local only.** Cheapest and safest, but leaves every Vultr claim unproven — all "architected," no
  "measured." Weak for the stated purpose.
- **Always-on Vultr.** Most impressive, but burns budget continuously (see
  [`infra/cost.md`](../../infra/cost.md): ~$79/week for an A16 left up) and puts a paid resource in
  the default path. Rejected.
- **Local default + plan-only IaC + one bounded real run.** Free by default; the full VKE/Object
  Storage topology is reviewable as `terraform plan`; a single minimal GPU is applied on demand for a
  real benchmark, then destroyed.

## Decision

Ship **both, with a hard default toward $0**:

- **Local ($0):** `docker compose up` runs the gateway, an Ollama/llama.cpp Q4 model, and Qdrant on
  one machine. This is the everyday path.
- **Vultr IaC, plan-only:** Terraform + Helm for **VKE + Object Storage** are shipped as reviewable
  code and stay `terraform plan` / `helm lint` only (`make tf-plan`, `make helm-lint`) — $0.
- **One bounded real A16 run:** a dedicated minimal **A16 GPU** module (`make bench-vultr`) is applied
  once — `apply` → serve vLLM → run the eval/benchmark harness → push results to Object Storage →
  **`destroy`** — so the leaderboard carries real Vultr latency/throughput/tokens-per-sec. It needs
  `TF_VAR_vultr_api_key`; the paid `apply` is **user-triggered**, never run automatically. Budget
  ~$2–10.

## Consequences

- **Positive:** free by default; Vultr claims are proven on real hardware; the interface is identical
  across both, so nothing downstream changes when a model moves from laptop to GPU.
- **Positive:** the cost/teardown discipline is itself a demonstrable operational habit.
- **Negative:** the multi-GPU tensor-parallel VKE topology is **architected and costed, not stood
  up** — the docs state this boundary plainly wherever the larger cluster is mentioned.
- **Negative:** the one real run requires a Vultr account + API key and manual authorization; it is
  not part of CI.
