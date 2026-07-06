.PHONY: help verify tf-plan helm-lint bench-vultr bench-vultr-cpu

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n", $$1, $$2}'

verify:  ## Run the full local verification ladder
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy sovereign gateway rag mcp_servers eval ci ide adoption
	uv run pytest -q

tf-plan:  ## terraform validate + plan (needs TF_VAR_vultr_api_key)
	cd infra/terraform && terraform init -input=false && terraform validate && terraform plan

helm-lint:  ## Lint the VKE Helm chart
	helm lint infra/helm/sovereign

bench-vultr:  ## Apply an A16, run the benchmark, then destroy (~$2–10; spends money)
	bash infra/scripts/bench-vultr.sh

bench-vultr-cpu:  ## Apply a CPU instance, benchmark, then destroy (~cents; no GPU needed)
	bash infra/scripts/bench-vultr-cpu.sh
