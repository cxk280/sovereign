# inference

Model-serving backends behind the [`gateway`](../gateway).

- **Local ($0 dev):** Ollama or llama.cpp serving a small **Q4 Qwen2.5-Coder** on CPU — the runnable
  demo path on a laptop.
- **Production target (Vultr Cloud GPU):** **vLLM**, OpenAI-compatible, CUDA / multi-GPU. Deployed via
  [`infra/`](../infra) Helm charts.
- **SGLang** and **TGI** are evaluated as alternatives in [`docs/`](../docs) ADRs (all three are
  first-class serving options for this platform).

_Built in build-order Step 1; vLLM/Helm target wired in Step 7._
