#!/usr/bin/env bash
# The GPU-less benchmark run: apply just a CPU cloud-compute instance, wait for
# Ollama to serve the model, run the eval/benchmark harness against it, then
# DESTROY. Budget ~cents (no GPU) — cheap enough for a few dollars of credit and
# no GPU access required. Requires TF_VAR_vultr_api_key. Mirrors bench-vultr.sh.
set -euo pipefail

cd "$(dirname "$0")/../terraform"

cleanup() {
  echo "==> destroying ALL CPU benchmark resources (instance + firewall)"
  terraform destroy \
    -target=vultr_instance.cpu_bench \
    -target=vultr_firewall_rule.cpu_gateway \
    -target=vultr_firewall_rule.cpu_ssh \
    -target=vultr_firewall_group.sovereign_cpu \
    -auto-approve
}
trap cleanup EXIT INT TERM

terraform init -input=false
terraform apply \
  -target=vultr_instance.cpu_bench \
  -target=vultr_firewall_group.sovereign_cpu \
  -target=vultr_firewall_rule.cpu_ssh \
  -target=vultr_firewall_rule.cpu_gateway \
  -auto-approve

IP="$(terraform output -raw cpu_bench_ip)"
BASE="http://${IP}:8000"

# Bounded wait for readiness. Unlike vLLM (which serves its model as soon as the
# API is up), Ollama's /v1/models lists the model only AFTER cloud-init finishes
# pulling it — so wait for the model to appear, not just for the endpoint to
# answer. If it isn't ready within READY_TIMEOUT, abort so the trap destroys the
# instance instead of billing on a stuck boot/download.
MODEL="qwen2.5-coder:1.5b"
READY_TIMEOUT="${READY_TIMEOUT:-1800}" # 30 min default
echo "==> waiting for Ollama to serve ${MODEL} at ${BASE} (install+pull can take several minutes; timeout ${READY_TIMEOUT}s)"
deadline=$(($(date +%s) + READY_TIMEOUT))
until curl -sf "${BASE}/v1/models" 2>/dev/null | grep -q "qwen2.5-coder"; do
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "!! ${MODEL} not served within ${READY_TIMEOUT}s — aborting; cleanup will destroy the instance" >&2
    exit 1
  fi
  sleep 15
done
echo "==> Ollama is serving ${MODEL}"

# CPU inference is far slower than a GPU, so give each request more headroom than
# the harness default (120s) to avoid a timeout sinking the run.
echo "==> running eval + benchmark against the real Vultr CPU instance"
cd ../..
SOVEREIGN_GATEWAY_URL="${BASE}" SOVEREIGN_EVAL_TIMEOUT="${SOVEREIGN_EVAL_TIMEOUT:-600}" \
  uv run python -m eval \
  --models "${MODEL}" \
  --gateway "${BASE}" \
  --out eval/results \
  --bench \
  --bench-host vultr-cpu

echo "==> done; results in eval/results/ (cleanup runs on exit)"
