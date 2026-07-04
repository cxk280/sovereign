# ci

AI-assisted CI/CD jobs, called by [`.gitlab-ci.yml`](../.gitlab-ci.yml) on merge requests. Each job
fetches the MR diff, asks the internal [`gateway`](../gateway) — **no code leaves for a third-party
AI** — and posts a note back to GitLab.

| Job | Module | Posts |
|---|---|---|
| AI code review | `ci.review` | inline review of correctness/security/style issues |
| Test generation | `ci.testgen` | suggested pytest tests for the changed code |
| MR summary | `ci.summary` | a 3–5 bullet summary for reviewers |

The gateway and GitLab clients are **injected** into each job's `run()` (see `_job.py`), so the
logic is unit-tested with fakes; `run_from_env()` wires the real clients from GitLab CI variables.

## Running live

1. Mirror this repo to GitLab (the `gitlab` remote) so `.gitlab-ci.yml` executes there.
2. Set CI/CD variables: **`GITLAB_TOKEN`** (`api` scope) and **`SOVEREIGN_GATEWAY_URL`**.
3. Use a runner that can reach the gateway (e.g. a self-hosted runner on your network, or the gateway
   deployed on Vultr — Step 7). Open an MR and the three notes appear.

The public GitHub mirror runs a thin lint/type/test + secret-scan pipeline
([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)).
