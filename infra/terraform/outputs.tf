output "gpu_bench_ip" {
  value       = vultr_instance.gpu_bench.main_ip
  description = "Public IP of the A16 benchmark instance (vLLM on :8000)."
}

output "vke_kubeconfig" {
  value       = var.enable_vke ? vultr_kubernetes.vke[0].kube_config : ""
  sensitive   = true
  description = "VKE kubeconfig (empty unless enable_vke = true)."
}

output "object_storage_hostname" {
  value       = var.enable_object_storage ? vultr_object_storage.artifacts[0].s3_hostname : ""
  description = "S3-compatible endpoint for artifacts (empty unless enabled)."
}
