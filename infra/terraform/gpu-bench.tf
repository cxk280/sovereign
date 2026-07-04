# The ONE resource intended to be applied — a minimal A16 GPU instance for the
# benchmark run (apply → serve vLLM → run the harness → destroy). See
# scripts/bench-vultr.sh and cost.md. cloud-init makes it benchmark-ready on boot.

resource "vultr_firewall_group" "sovereign" {
  description = "sovereign benchmark"
}

resource "vultr_firewall_rule" "ssh" {
  firewall_group_id = vultr_firewall_group.sovereign.id
  protocol          = "tcp"
  ip_type           = "v4"
  subnet            = "0.0.0.0"
  subnet_size       = 0
  port              = "22"
}

resource "vultr_firewall_rule" "gateway" {
  firewall_group_id = vultr_firewall_group.sovereign.id
  protocol          = "tcp"
  ip_type           = "v4"
  subnet            = "0.0.0.0"
  subnet_size       = 0
  port              = "8000"
}

resource "vultr_instance" "gpu_bench" {
  region            = var.region
  plan              = var.gpu_plan
  os_id             = var.os_id
  label             = "sovereign-a16-bench"
  hostname          = "sovereign-a16-bench"
  ssh_key_ids       = var.ssh_key_ids
  firewall_group_id = vultr_firewall_group.sovereign.id
  user_data         = base64encode(file("${path.module}/cloud-init/vllm.yaml"))
  tags              = ["sovereign", "benchmark", "ephemeral"]
}
