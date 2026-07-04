#!/usr/bin/env bash
# The real A16 benchmark run: apply just the GPU instance, wait for vLLM, run the
# eval/benchmark harness against it, then DESTROY. Budget ~$2–10. Requires
# TF_VAR_vultr_api_key. This spends money — run deliberately.
set -euo pipefail

cd "$(dirname "$0")/../terraform"

cleanup() {
  echo "==> destroying benchmark instance"
  terraform destroy -target=vultr_instance.gpu_bench -target=vultr_firewall_group.sovereign -auto-approve
}
trap cleanup EXIT

terraform init -input=false
terraform apply \
  -target=vultr_instance.gpu_bench \
  -target=vultr_firewall_group.sovereign \
  -target=vultr_firewall_rule.ssh \
  -target=vultr_firewall_rule.gateway \
  -auto-approve

IP="$(terraform output -raw gpu_bench_ip)"
BASE="http://${IP}:8000"
echo "==> waiting for vLLM at ${BASE} (model download can take several minutes)"
until curl -sf "${BASE}/v1/models" >/dev/null; do sleep 15; done

echo "==> running eval + benchmark against the real A16"
cd ../..
SOVEREIGN_GATEWAY_URL="${BASE}" uv run python -m eval \
  --models "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ" \
  --gateway "${BASE}" \
  --out eval/results

echo "==> done; results in eval/results/ (cleanup runs on exit)"
