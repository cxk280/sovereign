"""ci — AI-assisted CI/CD jobs, invoked by .gitlab-ci.yml on merge requests.

Each job fetches the MR diff, asks the internal gateway (no third-party AI), and
posts a note back to GitLab: automated code review, test generation, and MR
summaries. The gateway and GitLab clients are injected into each job's ``run``
function so the logic is unit-tested with fakes (no network).
"""
