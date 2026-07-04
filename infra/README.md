# infra

Infrastructure as code to deploy `sovereign` on **Vultr** — shipped as reviewable IaC and cost
estimates, **not** live spend (`terraform validate` + `terraform plan` only; nothing applied).

- **Terraform** — Vultr Cloud GPU instance(s), **VKE** (Kubernetes) cluster, **Object Storage** bucket
  (model artifacts + eval reports), firewall, load balancer.
- **Helm charts** — vLLM, gateway, Qdrant, dashboard on VKE.
- **Cost estimates** — per-component monthly cost for the reference deployment.

_Built in build-order Step 7._
