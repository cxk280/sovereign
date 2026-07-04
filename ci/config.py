"""Read GitLab CI/CD environment into a typed config."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class CIConfig:
    gateway_url: str
    api_url: str
    project_id: str
    mr_iid: str
    token: str


def from_env() -> CIConfig:
    return CIConfig(
        gateway_url=os.environ.get("SOVEREIGN_GATEWAY_URL", "http://localhost:8080"),
        api_url=os.environ["CI_API_V4_URL"],
        project_id=os.environ["CI_PROJECT_ID"],
        mr_iid=os.environ["CI_MERGE_REQUEST_IID"],
        token=os.environ["GITLAB_TOKEN"],
    )
