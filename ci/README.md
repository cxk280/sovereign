# ci

AI-assisted CI/CD jobs, called by [`.gitlab-ci.yml`](../.gitlab-ci.yml) on the GitLab mirror. Each
job calls the internal [`gateway`](../gateway) endpoint — no code leaves the org to a third-party AI.

- **code-review** — posts inline review comments on a merge request.
- **test-gen** — proposes tests for changed files.
- **mr-summary** — writes a concise merge-request summary.

The public GitHub mirror runs a thin lint/type/test + secret-scan pipeline
([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) and links to the live GitLab pipelines.

_Built in build-order Step 4._
