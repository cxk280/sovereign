variable "vultr_api_key" {
  type        = string
  sensitive   = true
  description = "Vultr API key (export TF_VAR_vultr_api_key; never commit)."
}

variable "region" {
  type        = string
  default     = "ewr"
  description = "Vultr region id (ewr = New Jersey)."
}

# Illustrative A16 GPU plan id — confirm the current id in the Vultr API/console
# before applying. A16 (16 GB) is the sweet spot for a 1.5B–7B quantized coder model.
variable "gpu_plan" {
  type        = string
  default     = "vcg-a16-2c-8gb-2vram"
  description = "Vultr Cloud GPU plan id for the benchmark instance."
}

variable "os_id" {
  type        = number
  default     = 1743 # Ubuntu 22.04 LTS x64 (confirm current id)
  description = "Vultr OS id."
}

variable "ssh_key_ids" {
  type        = list(string)
  default     = []
  description = "Vultr SSH key ids to install on the benchmark instance."
}

# Cost-control switches: the platform (VKE + Object Storage) is plan-only by
# default; only the GPU benchmark instance is meant to be applied.
variable "enable_vke" {
  type        = bool
  default     = false
  description = "Create the VKE cluster (leave false for plan-only / $0)."
}

variable "enable_object_storage" {
  type        = bool
  default     = false
  description = "Create the Object Storage bucket for artifacts/eval reports."
}

variable "object_storage_cluster_id" {
  type        = number
  default     = 2 # illustrative; list clusters via the Vultr API
  description = "Vultr Object Storage cluster id."
}

variable "object_storage_tier_id" {
  type        = number
  default     = 1 # illustrative; list tiers via the Vultr API
  description = "Vultr Object Storage tier id."
}
