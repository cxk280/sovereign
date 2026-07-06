#!/usr/bin/env bash
# The real A16 benchmark run: apply just the GPU instance, wait for vLLM, run the
# eval/benchmark harness against it, then DESTROY. Budget ~$2–10. Requires
# TF_VAR_vultr_api_key. This spends money — run deliberately.
set -euo pipefail

# Resolve absolute paths up front so cleanup is cwd-independent: the eval step
# below runs from the repo root, and the EXIT/INT/TERM trap inherits that cwd —
# so terraform must be told its dir explicitly (-chdir) or destroy would run
# against no config and leak a running, billing GPU instance.
TF_DIR="$(cd "$(dirname "$0")/../terraform" && pwd)"
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

cleanup() {
  echo "==> destroying ALL benchmark resources (instance + firewall)"
  terraform -chdir="$TF_DIR" destroy \
    -target=vultr_instance.gpu_bench \
    -target=vultr_firewall_rule.gateway \
    -target=vultr_firewall_rule.ssh \
    -target=vultr_firewall_group.sovereign \
    -auto-approve
}
trap cleanup EXIT INT TERM

terraform -chdir="$TF_DIR" init -input=false
terraform -chdir="$TF_DIR" apply \
  -target=vultr_instance.gpu_bench \
  -target=vultr_firewall_group.sovereign \
  -target=vultr_firewall_rule.ssh \
  -target=vultr_firewall_rule.gateway \
  -auto-approve

IP="$(terraform -chdir="$TF_DIR" output -raw gpu_bench_ip)"
BASE="http://${IP}:8000"

# Bounded wait: if vLLM isn't serving within READY_TIMEOUT, abort so the trap
# destroys the instance instead of billing forever on a stuck boot/download.
READY_TIMEOUT="${READY_TIMEOUT:-1800}"  # 30 min default
echo "==> waiting for vLLM at ${BASE} (model download can take several minutes; timeout ${READY_TIMEOUT}s)"
deadline=$(( $(date +%s) + READY_TIMEOUT ))
until curl -sf "${BASE}/v1/models" >/dev/null; do
  if [ "$(date +%s)" -ge "$deadline" ]; then
    echo "!! vLLM not ready within ${READY_TIMEOUT}s — aborting; cleanup will destroy the instance" >&2
    exit 1
  fi
  sleep 15
done
echo "==> vLLM is serving"

echo "==> running eval + benchmark against the real A16"
cd "$REPO_ROOT"
SOVEREIGN_GATEWAY_URL="${BASE}" uv run python -m eval \
  --models "Qwen/Qwen2.5-Coder-7B-Instruct-AWQ" \
  --gateway "${BASE}" \
  --out eval/results \
  --bench \
  --bench-host vultr-a16

echo "==> done; results in eval/results/ (cleanup runs on exit)"
