# infra

Infrastructure as code to run `sovereign` on **Vultr**. The platform (VKE + Object Storage) ships as
reviewable IaC that stays **plan-only** ($0); a minimal **A16 GPU instance** is meant to be applied
once for a real benchmark, then destroyed.

```
infra/
├── terraform/         # Vultr provider, variables, GPU-bench instance, VKE + Object Storage
│   ├── gpu-bench.tf   # the A16 instance + firewall — the one thing you apply
│   ├── platform.tf    # VKE + Object Storage (count=0 until enable_* = true)
│   └── cloud-init/    # boots vLLM (AWQ Qwen2.5-Coder) on the A16, OpenAI-compatible :8000
├── helm/sovereign/    # VKE chart: gateway, qdrant, vllm (tensor-parallel), dashboard
├── scripts/bench-vultr.sh  # apply → wait for vLLM → run eval/bench → destroy
└── cost.md            # cost estimate + the ~$5–10 benchmark budget
```

## Plan-only (free)

```bash
make tf-plan     # terraform validate + plan (needs TF_VAR_vultr_api_key)
make helm-lint   # lint the VKE chart
```

## The real A16 benchmark run (~$2–10, spends money)

```bash
export TF_VAR_vultr_api_key=...      # and set ssh_key_ids in terraform.tfvars
make bench-vultr                     # apply A16 → benchmark → destroy
```

It serves an AWQ-quantized coder model with vLLM on the A16, runs `python -m eval` against it so the
leaderboard carries **measured** Vultr numbers, and tears the instance down on exit. Multi-GPU
(tensor-parallel) serving is expressed in the Helm `values.yaml` (`vllm.gpus > 1`) but not stood up in
the $0 build — see [`cost.md`](./cost.md).

_Built in build-order Step 7._
