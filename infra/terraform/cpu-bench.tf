# A GPU-less CPU alternative to gpu-bench.tf: a regular cloud-compute instance
# that serves the quantized coder model with Ollama (apply → serve → run the
# harness → destroy). It produces REAL measured numbers on Vultr for a few cents
# — no GPU credit required. See scripts/bench-vultr-cpu.sh and cost.md.
#
# It has its OWN firewall group (not the gpu-bench group) so tearing down a CPU
# run never touches a GPU run and vice-versa. cloud-init/ollama.yaml makes it
# benchmark-ready on boot, serving the OpenAI-compatible API on :8000.

resource "vultr_firewall_group" "sovereign_cpu" {
  description = "sovereign cpu benchmark"
}

resource "vultr_firewall_rule" "cpu_ssh" {
  firewall_group_id = vultr_firewall_group.sovereign_cpu.id
  protocol          = "tcp"
  ip_type           = "v4"
  subnet            = "0.0.0.0"
  subnet_size       = 0
  port              = "22"
}

resource "vultr_firewall_rule" "cpu_gateway" {
  firewall_group_id = vultr_firewall_group.sovereign_cpu.id
  protocol          = "tcp"
  ip_type           = "v4"
  subnet            = "0.0.0.0"
  subnet_size       = 0
  port              = "8000"
}

resource "vultr_instance" "cpu_bench" {
  region            = var.region
  plan              = var.cpu_plan
  os_id             = var.os_id
  label             = "sovereign-cpu-bench"
  hostname          = "sovereign-cpu-bench"
  ssh_key_ids       = var.ssh_key_ids
  firewall_group_id = vultr_firewall_group.sovereign_cpu.id
  user_data         = base64encode(file("${path.module}/cloud-init/ollama.yaml"))
  tags              = ["sovereign", "benchmark", "cpu", "ephemeral"]
}
