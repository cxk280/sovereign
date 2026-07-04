# Production platform — VKE (Kubernetes) + Object Storage. Plan-only by default
# (count = 0) to keep spend at $0; flip the enable_* variables to provision.

resource "vultr_kubernetes" "vke" {
  count   = var.enable_vke ? 1 : 0
  region  = var.region
  version = "v1.30.0+1"
  label   = "sovereign-vke"

  node_pools {
    node_quantity = 2
    plan          = "vc2-4c-8gb"
    label         = "sovereign-pool"
  }
}

resource "vultr_object_storage" "artifacts" {
  count      = var.enable_object_storage ? 1 : 0
  cluster_id = var.object_storage_cluster_id
  tier_id    = var.object_storage_tier_id
  label      = "sovereign-artifacts"
}
